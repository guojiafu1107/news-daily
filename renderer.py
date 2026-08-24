def render_html(news_data):
    date_str = news_data.get("_date", "")

    sections = ""

    for cat_name, cat_data in news_data.items():
        if not isinstance(cat_data, dict) or "sources" not in cat_data:
            continue

        color = cat_data.get("color", "#333")
        cards = ""

        for src_name, src_info in cat_data["sources"].items():
            items = src_info.get("items", [])
            translated = src_info.get("translated", [])
            is_english = src_info.get("is_english", False)

            for idx, it in enumerate(items):
                title = it.get("title", "")
                url = it.get("url", "#")

                if is_english and idx < len(translated):
                    # 英文：原文 + 译文双行对照
                    zh = translated[idx]
                    cards += f"""
<div style="margin-bottom:14px;padding:12px 16px;background:#fff;border-radius:8px;border-left:4px solid {color};box-shadow:0 1px 3px rgba(0,0,0,.05);">
  <div style="margin-bottom:5px;">
    <span style="display:inline-block;background:{color};color:#fff;font-size:11px;padding:2px 8px;border-radius:3px;margin-right:5px;">📌 {src_name}</span>
    <span style="display:inline-block;background:#f9a825;color:#fff;font-size:10px;padding:1px 5px;border-radius:3px;">译</span>
  </div>
  <div style="color:#888;font-size:12px;margin-bottom:4px;font-style:italic;">{title}</div>
  <a href="{url}" style="color:#1a0dab;text-decoration:none;font-size:14px;line-height:1.6;font-weight:500;">{zh}</a>
</div>"""
                else:
                    # 中文：来源标签 + 标题
                    cards += f"""
<div style="margin-bottom:14px;padding:12px 16px;background:#fff;border-radius:8px;border-left:4px solid {color};box-shadow:0 1px 3px rgba(0,0,0,.05);">
  <div style="margin-bottom:5px;">
    <span style="display:inline-block;background:{color};color:#fff;font-size:11px;padding:2px 8px;border-radius:3px;">📌 {src_name}</span>
  </div>
  <a href="{url}" style="color:#1a0dab;text-decoration:none;font-size:14px;line-height:1.6;">{title}</a>
</div>"""

        sections += f"""
<div style="margin-bottom:28px;">
  <h2 style="color:{color};font-size:18px;margin-bottom:14px;border-bottom:2px solid {color};padding-bottom:6px;">{cat_name}</h2>
  {cards}
</div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>每日新闻速递</title>
</head>
<body style="margin:0;padding:20px;background:#f0f2f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<div style="max-width:700px;margin:0 auto;background:#fff;border-radius:12px;padding:28px;box-shadow:0 2px 12px rgba(0,0,0,.08);">
  <div style="text-align:center;margin-bottom:24px;">
    <h1 style="color:#1a1a1a;font-size:22px;margin:0;">📰 每日新闻速递</h1>
    <p style="color:#888;font-size:13px;margin:6px 0 0;">{date_str} · 10 个国内权威源 · 各 10 条</p>
  </div>
  {sections}
  <div style="text-align:center;color:#aaa;font-size:11px;margin-top:32px;padding-top:16px;border-top:1px solid #eee;">
    由智谱 GLM-4-Flash 提供翻译 · 自动生成
  </div>
</div>
</body>
</html>"""
    return html