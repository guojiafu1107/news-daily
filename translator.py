"""
智谱 GLM 翻译模块
使用智谱 AI 免费模型将英文翻译为中文
"""
import os
import time
from zhipuai import ZhipuAI


def get_client():
    api_key = os.environ.get("ZHIPU_API_KEY")
    if not api_key:
        raise RuntimeError("环境变量 ZHIPU_API_KEY 未设置")
    return ZhipuAI(api_key=api_key)


def translate_text(text: str, client=None) -> str:
    """单条文本翻译，英文→中文"""
    if not text or not text.strip():
        return ""
    # 粗略判断是否需要翻译
    if not _looks_english(text):
        return text

    if client is None:
        try:
            client = get_client()
        except RuntimeError:
            # 无 API Key 时优雅降级，保留原文
            return text

    prompt = f"请将以下英文新闻标题翻译为简体中文，只输出翻译结果，不要解释：\n\n{text.strip()}"
    try:
        resp = client.chat.completions.create(
            model="glm-4-flash",  # 智谱免费模型
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512,
        )
        result = resp.choices[0].message.content.strip()
        # 简单清理
        result = result.strip("\"'。.")
        return result
    except Exception as e:
        print(f"[翻译失败] {e} → 保留原文")
        return text


def translate_batch(texts: list[str], client=None) -> list[str]:
    """批量翻译，带简单限流"""
    if client is None:
        client = get_client()
    results = []
    for i, t in enumerate(texts):
        results.append(translate_text(t, client))
        if i < len(texts) - 1:
            time.sleep(0.5)  # 避免触发限流
    return results


def _looks_english(text: str) -> bool:
    """判断文本是否主要为英文"""
    ascii_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    total = sum(1 for c in text if c.isalpha())
    if total == 0:
        return False
    return ascii_chars / total > 0.6
