"""
新闻抓取模块 v2
- 增强 UA 伪装 + 重试
- 优先尝试 RSS / JSON 接口（更稳、更轻）
- 兜底 HTML 解析
"""
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from typing import Optional

# ---------- 请求层 ----------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

SESSION = requests.Session()

def _headers(referer: str = "") -> dict:
    h = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    if referer:
        h["Referer"] = referer
    return h

def _get(url: str, timeout: int = 20, retries: int = 3) -> Optional[str]:
    for attempt in range(1, retries + 1):
        try:
            r = SESSION.get(url, headers=_headers(url), timeout=timeout, allow_redirects=True)
            if r.status_code == 403:
                # 403 时换 UA 重试
                print(f"  [403] 第 {attempt} 次，换 UA 重试 ...")
                SESSION.headers.update({"User-Agent": random.choice(USER_AGENTS)})
                time.sleep(2 * attempt)
                continue
            r.raise_for_status()
            # 编码探测
            for enc in ("utf-8", "gbk", "gb2312", "big5", "iso-8859-1"):
                try:
                    r.encoding = enc
                    r.text
                    break
                except Exception:
                    continue
            return r.text
        except Exception as e:
            print(f"  [抓取异常] {url} 第 {attempt} 次: {e}")
            time.sleep(3 * attempt)
    return None

def _get_json(url: str, timeout: int = 20) -> Optional[dict]:
    try:
        r = SESSION.get(url, headers=_headers(url), timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [JSON 获取失败] {url}: {e}")
        return None

# ---------- 通用解析工具 ----------

def _clean(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    # 去掉常见噪音
    text = re.sub(r"^(Breaking|Live|UPDATE):\s*", "", text, flags=re.I)
    return text

def _dedup(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        t = it["title"].strip().lower()
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(it)
    return out

def _abs(url: str, base: str) -> str:
    if url.startswith("http"):
        return url
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return base.rstrip("/") + url
    return base.rstrip("/") + "/" + url

# ---------- 通用 HTML 抽取（兜底） ----------

def _extract_from_html(html: str, base_url: str, min_len: int = 8,
                      url_must_contain: list[str] | None = None,
                      url_must_not: list[str] | None = None) -> list[dict]:
    """通用：从 HTML 中提取所有合规链接标题"""
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    items = []
    url_must = url_must_contain or []
    url_skip = url_must_not or []

    for a in soup.select("a[href]"):
        text = _clean(a.get_text())
        href = a["href"].strip()
        if len(text) < min_len:
            continue
        if any(s in href.lower() for s in url_skip):
            continue
        if url_must and not any(re.search(p, href) for p in url_must):
            continue
        items.append({"title": text, "url": _abs(href, base_url)})
    return _dedup(items)[:10]

# ============================================================
#  各新闻源（优先 RSS/API，兜底 HTML）
# ============================================================

# --- 联合早报 ---
ZAOBAO_RSS = "https://www.zaobao.com/realtime/world/feed"
ZAOBAO_HTML = "https://www.zaobao.com/realtime/world"

def fetch_zaobao():
    items = []
    # 尝试 RSS
    data = _get(ZAOBAO_RSS)
    if data:
        try:
            soup = BeautifulSoup(data, "lxml-xml")
            for item in soup.select("item")[:10]:
                title = _clean(item.title.get_text()) if item.title else ""
                link = item.link.get_text().strip() if item.link else ""
                if title and link:
                    items.append({"title": title, "url": link})
        except Exception as e:
            print(f"  [RSS 解析失败] {e}")
    if not items:
        html = _get(ZAOBAO_HTML)
        items = _extract_from_html(
            html, "https://www.zaobao.com",
            min_len=8,
            url_must=[r"/realtime/", r"/news/"],
            url_skip=["javascript:", "#", "/search", "facebook", "twitter", "whatsapp", "telegram", ".xml"]
        )
    return {"name": "联合早报（国际）", "category": "中文国际", "items": items[:10]}

# --- 环球网 ---
HUANQIU_HTML = "https://world.huanqiu.com"

def fetch_huanqiu():
    html = _get(HUANQIU_HTML)
    items = _extract_from_html(
        html, "https://world.huanqiu.com",
        min_len=8,
        url_must=[r"/article/", r"/a/"],
        url_skip=["javascript:", "#", "/search", "facebook", "twitter", "weibo", "video", "live"]
    )
    return {"name": "环球网（国际）", "category": "中文国际", "items": items[:10]}

# --- 香港新闻网 ---
HKCNA_RSS = "https://www.hkcna.hk/rss.xml"
HKCNA_HTML = "https://www.hkcna.hk"

def fetch_hkcna():
    items = []
    data = _get(HKCNA_RSS)
    if data:
        try:
            soup = BeautifulSoup(data, "lxml-xml")
            for item in soup.select("item")[:10]:
                title = _clean(item.title.get_text()) if item.title else ""
                link = item.link.get_text().strip() if item.link else ""
                if title and link:
                    items.append({"title": title, "url": link})
        except Exception:
            pass
    if not items:
        html = _get(HKCNA_HTML)
        items = _extract_from_html(
            html, "https://www.hkcna.hk",
            min_len=8,
            url_must=[r"\d{4}/\d{2}/\d{2}", r"/news/", r"/content/"],
            url_skip=["javascript:", "#", "/search", "facebook", "twitter"]
        )
    return {"name": "香港新闻网", "category": "中文国际", "items": items[:10]}

# --- NHK World (EN) ---
NHK_RSS = "https://www3.nhk.or.jp/nhkworld/en/news/rss.xml"
NHK_HTML = "https://www3.nhk.or.jp/nhkworld/en/news/"

def fetch_nhk():
    items = []
    data = _get(NHK_RSS)
    if data:
        try:
            soup = BeautifulSoup(data, "lxml-xml")
            for item in soup.select("item")[:10]:
                title = _clean(item.title.get_text()) if item.title else ""
                link = item.link.get_text().strip() if item.link else ""
                if title and link:
                    items.append({"title": title, "url": link})
        except Exception:
            pass
    if not items:
        html = _get(NHK_HTML)
        items = _extract_from_html(
            html, "https://www3.nhk.or.jp",
            min_len=10,
            url_must=[r"/news/"],
            url_skip=["javascript:", "#", "/search", "/tag", "facebook", "twitter"]
        )
    return {"name": "NHK World", "category": "英文原版", "items": items[:10]}

# --- France 24 (EN) ---
FR24_RSS = "https://www.france24.com/en/rss"
FR24_HTML = "https://www.france24.com/en/"

def fetch_france24():
    items = []
    data = _get(FR24_RSS)
    if data:
        try:
            soup = BeautifulSoup(data, "lxml-xml")
            for item in soup.select("item")[:10]:
                title = _clean(item.title.get_text()) if item.title else ""
                link = item.link.get_text().strip() if item.link else ""
                if title and link:
                    items.append({"title": title, "url": link})
        except Exception:
            pass
    if not items:
        html = _get(FR24_HTML)
        items = _extract_from_html(
            html, "https://www.france24.com",
            min_len=10,
            url_must=[r"/en/"],
            url_skip=["javascript:", "#", "/search", "/tag", "/emission", "facebook", "twitter", "youtube"]
        )
    return {"name": "France 24", "category": "英文原版", "items": items[:10]}

# --- RT ---
RT_RSS = "https://www.rt.com/rss/"
RT_HTML = "https://www.rt.com"

def fetch_rt():
    items = []
    data = _get(RT_RSS)
    if data:
        try:
            soup = BeautifulSoup(data, "lxml-xml")
            for item in soup.select("item")[:10]:
                title = _clean(item.title.get_text()) if item.title else ""
                link = item.link.get_text().strip() if item.link else ""
                if title and link:
                    items.append({"title": title, "url": link})
        except Exception:
            pass
    if not items:
        html = _get(RT_HTML)
        items = _extract_from_html(
            html, "https://www.rt.com",
            min_len=10,
            url_must=[r"/news/", r"\d{4}/\d{2}/\d{2}/"],
            url_skip=["javascript:", "#", "/search", "/tag", "facebook", "twitter", "telegram"]
        )
    return {"name": "RT", "category": "英文原版", "items": items[:10]}

# --- FT 中文网 ---
FTC_RSS = "https://www.ftchinese.com/rss/feed"
FTC_HTML = "https://www.ftchinese.com"

def fetch_ftchinese():
    items = []
    data = _get(FTC_RSS)
    if data:
        try:
            soup = BeautifulSoup(data, "lxml-xml")
            for item in soup.select("item")[:10]:
                title = _clean(item.title.get_text()) if item.title else ""
                link = item.link.get_text().strip() if item.link else ""
                if title and link:
                    items.append({"title": title, "url": link})
        except Exception:
            pass
    if not items:
        html = _get(FTC_HTML)
        items = _extract_from_html(
            html, "https://www.ftchinese.com",
            min_len=8,
            url_must=[r"/story/", r"/premium/"],
            url_skip=["javascript:", "#", "/search", "facebook", "twitter", "weibo"]
        )
    return {"name": "FT 中文网", "category": "财经", "items": items[:10]}

# --- 华尔街日报中文版 ---
WSJ_RSS = "https://cn.wsj.com/public/page/rss-news.xml"
WSJ_HTML = "https://cn.wsj.com"

def fetch_wsjcn():
    items = []
    data = _get(WSJ_RSS)
    if data:
        try:
            soup = BeautifulSoup(data, "lxml-xml")
            for item in soup.select("item")[:10]:
                title = _clean(item.title.get_text()) if item.title else ""
                link = item.link.get_text().strip() if item.link else ""
                if title and link:
                    items.append({"title": title, "url": link})
        except Exception:
            pass
    if not items:
        html = _get(WSJ_HTML)
        items = _extract_from_html(
            html, "https://cn.wsj.com",
            min_len=8,
            url_skip=["javascript:", "#", "/search", "facebook", "twitter"]
        )
    return {"name": "华尔街日报中文版", "category": "财经", "items": items[:10]}

# --- 华尔街见闻 ---
WSCN_RSS = "https://wallstreetcn.com/rss.xml"
WSCN_HTML = "https://wallstreetcn.com"

def fetch_wallstreetcn():
    items = []
    data = _get(WSCN_RSS)
    if data:
        try:
            soup = BeautifulSoup(data, "lxml-xml")
            for item in soup.select("item")[:10]:
                title = _clean(item.title.get_text()) if item.title else ""
                link = item.link.get_text().strip() if item.link else ""
                if title and link:
                    items.append({"title": title, "url": link})
        except Exception:
            pass
    if not items:
        html = _get(WSCN_HTML)
        items = _extract_from_html(
            html, "https://wallstreetcn.com",
            min_len=8,
            url_must=[r"/articles/", r"/live/"],
            url_skip=["javascript:", "#", "/search", "facebook", "twitter"]
        )
    return {"name": "华尔街见闻", "category": "财经", "items": items[:10]}

# ============================================================
#  调度
# ============================================================

SOURCES = [
    ("中文国际", [fetch_zaobao, fetch_huanqiu, fetch_hkcna]),
    ("英文原版", [fetch_nhk,    fetch_france24, fetch_rt]),
    ("财经",     [fetch_ftchinese, fetch_wsjcn, fetch_wallstreetcn]),
]

def fetch_all() -> list[dict]:
    results = []
    for cat_name, fetchers in SOURCES:
        for fetcher in fetchers:
            try:
                print(f"[抓取] {fetcher.__name__} ...")
                data = fetcher()
                print(f"  → 获取 {len(data['items'])} 条")
                results.append(data)
            except Exception as e:
                print(f"  → 异常: {e}")
                results.append({"name": fetcher.__name__.replace("fetch_", ""),
                                "category": cat_name, "items": []})
            time.sleep(random.uniform(1.5, 3.0))
    return results
