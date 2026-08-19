"""
每日新闻聚合邮件 - 主入口
流程：抓取 → 翻译(英文源) → 渲染 HTML → 发送邮件
"""
import sys
import os
import time
from datetime import datetime, timedelta

# 确保同目录导入可用
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetcher import fetch_all
from translator import get_client, translate_batch
from renderer import render
from sender import send_email

def main():
    # 1. 抓取
    print("=" * 50)
    print("🚀 开始抓取新闻 ...")
    news_data = fetch_all()

    # 2. 翻译英文源
    print("\n" + "=" * 50)
    print("🌐 翻译英文源 ...")
    try:
        client = get_client()
        have_translator = True
    except RuntimeError as e:
        print(f"[警告] {e}，英文标题将保留原文")
        client = None
        have_translator = False

    if have_translator:
        for source in news_data:
            if source.get("category") != "英文原版":
                continue
            titles = [it["title"] for it in source["items"]]
            if not titles:
                continue
            print(f"  翻译 {source['name']} ({len(titles)} 条) ...")
            translated = translate_batch(titles, client)
            for item, t in zip(source["items"], translated):
                if t and t != item["title"]:
                    item["title"] = t
                    item["translated"] = True
                else:
                    item["translated"] = False
            time.sleep(1)

    # 3. 渲染
    print("\n" + "=" * 50)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    digest_date = f"{yesterday}（发送于 {today} 09:00）"
    print(f"📝 渲染邮件，日期：{digest_date}")
    html = render(news_data, digest_date)

    # 4. 保存本地副本（便于调试 / GitHub Actions Artifact）
    out_path = os.path.join(os.path.dirname(__file__), "latest_digest.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"💾 已保存预览：{out_path}")

    # 5. 发送
    print("\n" + "=" * 50)
    send_email(html)

    print("\n✅ 完成")


if __name__ == "__main__":
    main()
