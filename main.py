from datetime import datetime
from fetcher import fetch_all, ENGLISH_SOURCES
from translator import translate_batch
from renderer import render_html
from sender import send_email

def main():
    print("=" * 55)
    print("🚀 每日新闻速递 · 国内权威版")
    print("=" * 55)

    today = datetime.now().strftime("%Y-%m-%d")

    # 1. 抓取
    raw = fetch_all(limit=10)

    # 2. 翻译英文源
    print("🌐 翻译英文标题...")
    translated_map = {}
    for src in ENGLISH_SOURCES:
        items = raw.get(src, [])
        if items:
            titles = [it["title"] for it in items]
            print(f"    🔄 {src}: {len(titles)} 条")
            translated = translate_batch(titles)
            translated_map[src] = translated
    print("  🎉 翻译完成\n")

    # 3. 组织渲染数据（按分类）
    news_data = {
        "_date": today,
        "🌍 国际新闻": {
            "color": "#1a73e8",
            "sources": {
                "新华网·国际":    raw.get("新华网·国际", []),
                "央视网·国际":    raw.get("央视网·国际", []),
                "人民网·国际":    raw.get("人民网·国际", []),
                "中国新闻网·国际": raw.get("中国新闻网·国际", []),
            }
        },
        "🏛️ 时政要闻": {
            "color": "#6f42c1",
            "sources": {
                "新华网·时政": raw.get("新华网·时政", []),
                "央视网·国内": raw.get("央视网·国内", []),
                "人民网·要闻": raw.get("人民网·要闻", []),
            }
        },
        "💰 财经新闻": {
            "color": "#16a34a",
            "sources": {
                "新华网·财经":      raw.get("新华网·财经", []),
                "央视网·财经":      raw.get("央视网·财经", []),
                "中国新闻网·财经":   raw.get("中国新闻网·财经", []),
            }
        },
    }

    # 注入翻译结果和英文标记
    for cat_data in news_data.values():
        if isinstance(cat_data, dict) and "sources" in cat_data:
            for src_name, items in cat_data["sources"].items():
                cat_data["sources"][src_name] = {
                    "items": items,
                    "translated": translated_map.get(src_name, []),
                    "is_english": src_name in ENGLISH_SOURCES,
                }

    # 4. 渲染
    print("🎨 渲染邮件...")
    html = render_html(news_data)
    with open("latest_digest.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ 已保存 latest_digest.html")

    # 5. 发送
    print("\n📧 发送邮件...")
    try:
        send_email(html, today)
        print("\n🎉 全部完成！")
    except Exception as e:
        print(f"\n❌ 邮件发送失败: {e}")
        print("   HTML 已保存在 latest_digest.html，可手动打开查看")


if __name__ == "__main__":
    main()