import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36"
}

# ── 10 个国内权威源（全部直连可达）──────────────────
RSS_SOURCES = {
    # 🌍 国际（4个）
    "新华网·国际":      "http://xinhuanet.com/world/news_world.xml",
    "央视网·国际":      "http://english.cctv.com/service/rss/2/index.xml",
    "人民网·国际":      "http://world.people.com.cn/rss/world.xml",
    "中国新闻网·国际":   "http://chinanews.com.cn/rss/world.xml",
    # 🏛️ 时政（3个）
    "新华网·时政":      "http://xinhuanet.com/politics/news_politics.xml",
    "央视网·国内":      "http://english.cctv.com/service/rss/1/index.xml",
    "人民网·要闻":      "http://people.com.cn/rss/ywkx.xml",
    # 💰 财经（3个）
    "新华网·财经":      "http://xinhuanet.com/finance/news_finance.xml",
    "央视网·财经":      "http://english.cctv.com/service/rss/3/index.xml",
    "中国新闻网·财经":   "http://chinanews.com.cn/rss/finance.xml",
}

# 央视英文 RSS 源列表（需要翻译的）
ENGLISH_SOURCES = ["央视网·国际", "央视网·国内", "央视网·财经"]


def _get_with_retry(url, timeout=20, retries=2):
    """带重试的 GET 请求，支持代理"""
    proxies = {}
    https_proxy = os.getenv("HTTPS_PROXY")
    if https_proxy:
        proxies = {"https": https_proxy, "http": os.getenv("HTTP_PROXY", https_proxy)}
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout, proxies=proxies)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r
        except Exception as e:
            if attempt < retries:
                print(f"重试{attempt+1}...", end=" ")
                time.sleep(2)
            else:
                raise e


def _parse_rss(content, limit=10):
    """解析 RSS/Atom"""
    items = []
    soup = BeautifulSoup(content, "xml")
    # RSS 2.0
    for e in soup.find_all("item")[:limit]:
        title = e.find("title")
        link = e.find("link")
        if title and link:
            href = link.get_text(strip=True) if link.name == "link" else str(link.get("href", ""))
            if href and title.get_text(strip=True):
                items.append({"title": title.get_text(strip=True), "url": href})
    # Atom
    if not items:
        for e in soup.find_all("entry")[:limit]:
            title = e.find("title")
            link = e.find("link")
            if title and link:
                href = link.get("href", "")
                if href and title.get_text(strip=True):
                    items.append({"title": title.get_text(strip=True), "url": href})
    return items[:limit]


def _fetch_rss(name, url, limit=10):
    """抓取单个 RSS 源"""
    try:
        r = _get_with_retry(url)
        return _parse_rss(r.text, limit)
    except Exception as e:
        print(f"失败({type(e).__name__})", end="")
        return []


def fetch_all(limit=10):
    """抓取全部 10 个源"""
    print(f"\n📡 开始抓取（{datetime.now().strftime('%Y-%m-%d %H:%M')}）")
    print(f"   共 {len(RSS_SOURCES)} 个权威源，各取前 {limit} 条\n")

    result = {}
    for name, url in RSS_SOURCES.items():
        print(f"  🔍 {name}...", end=" ")
        items = _fetch_rss(name, url, limit)
        print(f"{len(items)} 条")
        result[name] = items

    total = sum(len(v) for v in result.values())
    en_count = sum(len(result.get(s, [])) for s in ENGLISH_SOURCES)
    zh_count = total - en_count
    print(f"\n  ✅ 合计抓取 {total} 条新闻")
    print(f"📊 统计：中文 {zh_count} 条 | 英文 {en_count} 条（将由智谱翻译为原文+译文对照）\n")

    return result