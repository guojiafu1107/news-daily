import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ZHIPU_API_KEY")
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


def _translate_one_batch(batch):
    """
    翻译一批英文标题。
    batch: list of str
    返回: list of str（与输入等长，失败返回原标题）
    """
    if not API_KEY:
        print("  ⚠️ 未配置 ZHIPU_API_KEY，跳过翻译")
        return batch

    # 过滤空标题，避免 400
    valid = [(i, t) for i, t in enumerate(batch) if t and t.strip()]
    if not valid:
        return batch

    lines = [t for _, t in valid]
    prompt = (
        "把以下英文新闻标题逐条翻译成中文，每行一条，"
        "只输出中文翻译，不要序号、不要解释、不要引号：\n\n"
        + "\n".join(lines)
    )

    payload = {
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        proxies = {}
        https_proxy = os.getenv("HTTPS_PROXY")
        if https_proxy:
            proxies = {"https": https_proxy}

        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30, proxies=proxies)
        resp.raise_for_status()

        data = resp.json()
        if "choices" not in data:
            print(f"  ⚠️ 响应异常: {data}")
            return batch

        text = data["choices"][0]["message"]["content"].strip()
        translated_lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 对齐数量
        result = batch.copy()
        for idx, (orig_idx, _) in enumerate(valid):
            if idx < len(translated_lines):
                result[orig_idx] = translated_lines[idx]

        return result

    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = e.response.json()
        except Exception:
            error_detail = e.response.text
        print(f"\n  ❌ HTTP {e.response.status_code}: {error_detail}")
        if e.response.status_code == 400:
            print("  ⚠️ 参数错误，降级使用原标题")
        return batch

    except Exception as e:
        print(f"\n  ❌ 翻译异常: {e}")
        return batch


def translate_batch(titles, batch_size=5):
    """
    批量翻译入口，供 main.py 调用。
    titles: list of str
    返回: list of str
    """
    if not titles:
        return []

    results = []
    total = len(titles)
    batches = (total + batch_size - 1) // batch_size

    for i in range(0, total, batch_size):
        batch = titles[i:i + batch_size]
        current = i // batch_size + 1
        print(f"    🔄 批次 {current}/{batches}（{len(batch)} 条）")
        translated = _translate_one_batch(batch)
        results.extend(translated)

    print(f"  ✅ 翻译完成 {len(results)} 条")
    return results