"""
HTML 邮件渲染模块
将抓取+翻译后的新闻数据渲染为美观的 HTML 邮件
"""
from datetime import datetime

CSS = """
<style>
  body { font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; max-width: 760px; margin: 0 auto; padding: 24px; color: #1a1a1a; background: #f7f8fa; }
  h1 { font-size: 22px; margin: 0 0 4px; color: #0f172a; }
  .subtitle { color: #64748b; font-size: 13px; margin-bottom: 24px; }
  .section { background: #fff; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
  .section h2 { font-size: 16px; margin: 0 0 14px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0; color: #0f766e; }
  .source-block { margin-bottom: 16px; }
  .source-block:last-child { margin-bottom: 0; }
  .source-name { font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 6px; }
  .news-list { list-style: none; padding: 0; margin: 0; }
  .news-list li { padding: 7px 0; border-bottom: 1px dashed #f1f5f9; font-size: 14px; line-height: 1.6; }
  .news-list li:last-child { border-bottom: none; }
  .news-list a { color: #1e293b; text-decoration: none; }
  .news-list a:hover { color: #0f766e; }
  .badge { display: inline-block; font-size: 11px; background: #e0f2fe; color: #0369a1; padding: 1px 6px; border-radius: 4px; margin-right: 6px; vertical-align: middle; }
  .badge-translated { background: #fef3c7; color: #92400e; }
  .empty { color: #94a3b8; font-size: 13px; font-style: italic; }
  .footer { text-align: center; color: #94a3b8; font-size: 12px; margin-top: 28px; }
</style>
"""

def render(news_data: list[dict], digest_date: str) -> str:
    """渲染完整 HTML 邮件"""
    sections_html = ""
    for source in news_data:
        name = source.get("name", "未知来源")
        items = source.get("items", [])
        cat = source.get("category", "")

        if not items:
            items_html = '<p class="empty">（本次未获取到内容）</p>'
        else:
            lis = []
            for it in items:
                title = it.get("title", "")
                url = it.get("url", "#")
                translated = it.get("translated", False)
                badge = ""
                if translated:
                    badge = '<span class="badge badge-translated">译</span>'
                lis.append(f'<li>{badge}<a href="{url}" target="_blank" rel="noopener">{title}</a></li>')
            items_html = f'<ul class="news-list">{"".join(lis)}</ul>'

        sections_html += f"""
        <div class="source-block">
          <div class="source-name">📰 {name}</div>
          {items_html}
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{CSS}
</head>
<body>
  <h1>🗞️ 每日新闻速递</h1>
  <div class="subtitle">{digest_date} · 自动聚合 · 中文国际 / 英文原版 / 财经</div>

  <div class="section">
    <h2>🌏 中文国际新闻</h2>
    {_filter_section(news_data, "中文国际", sections_html)}
  </div>

  <div class="section">
    <h2>🌐 英文原版（已翻译）</h2>
    {_filter_section(news_data, "英文原版", sections_html)}
  </div>

  <div class="section">
    <h2>💰 财经</h2>
    {_filter_section(news_data, "财经", sections_html)}
  </div>

  <div class="footer">
    由 GitHub Actions 自动生成 · 智谱 GLM 翻译 · 仅供个人阅读
  </div>
</body>
</html>"""
    return html


def _filter_section(news_data, category, _unused):
    """只渲染指定分类"""
    parts = ""
    for source in news_data:
        if source.get("category") != category:
            continue
        name = source.get("name", "未知来源")
        items = source.get("items", [])
        if not items:
            items_html = '<p class="empty">（本次未获取到内容）</p>'
        else:
            lis = []
            for it in items:
                title = it.get("title", "")
                url = it.get("url", "#")
                translated = it.get("translated", False)
                badge = '<span class="badge badge-translated">译</span>' if translated else ""
                lis.append(f'<li>{badge}<a href="{url}" target="_blank" rel="noopener">{title}</a></li>')
            items_html = f'<ul class="news-list">{"".join(lis)}</ul>'
        parts += f"""
        <div class="source-block">
          <div class="source-name">📰 {name}</div>
          {items_html}
        </div>
        """
    return parts
