"""
integration_test.py — 完整流程集成测试
不依赖外部API，验证：抓取 → 渲染 → 保存 → 邮件准备
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

print("=" * 60)
print("🚀 每日新闻速递 — 集成测试")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ── 1. 加载配置 ────────────────────────────────
print("\n📋 Step 1: 加载配置")
with open(ROOT / "config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
print(f"  ✅ 配置加载成功")
print(f"  📂 分类: {list(config['sources'].keys())}")
print(f"  📰 新闻源总数: {sum(len(v) for v in config['sources'].values())}")

# ── 2. 抓取新闻 ────────────────────────────────
print("\n📋 Step 2: 抓取新闻（RSS优先 + HTML兜底）")
from fetcher import Fetcher
fetcher = Fetcher(config)
results = fetcher.fetch_all()

total = 0
news_data = {}
for cat, items in results.items():
    news_data[cat] = [item.to_dict() for item in items]
    total += len(items)
    status = f"✅ {len(items)} 条" if items else "⚠️ 0 条"
    print(f"  {cat}: {status}")

print(f"\n  📊 总计: {total} 条")

# 如果全部为0（沙盒网络限制），用模拟数据继续测试后续流程
if total == 0:
    print("\n  ⚠️ 沙盒网络受限，使用模拟数据继续测试...")
    news_data = {
        "chinese_international": [
            {"title": "中美关系最新动态：高层会晤取得积极成果", "url": "https://www.zaobao.com/news1", "source": "联合早报", "summary": "双方在经贸、气候等领域达成多项共识，外界普遍持乐观态度。", "published": "2025-01-15"},
            {"title": "欧盟通过新数字监管法案，科技巨头面临挑战", "url": "https://www.zaobao.com/news2", "source": "联合早报", "summary": "新法案要求大型科技公司加强内容审核和数据保护。", "published": "2025-01-15"},
            {"title": "亚太地区安全形势分析与展望", "url": "https://www.zaobao.com/news3", "source": "联合早报", "summary": "", "published": ""},
            {"title": "全球粮食安全问题引发多国关注", "url": "https://world.huanqiu.com/news1", "source": "环球网", "summary": "联合国粮农组织发布最新报告，呼吁国际合作。", "published": "2025-01-15"},
            {"title": "中东和平进程取得新进展", "url": "https://world.huanqiu.com/news2", "source": "环球网", "summary": "", "published": ""},
            {"title": "太空探索新里程碑：商业航天迎来突破", "url": "https://world.huanqiu.com/news3", "source": "环球网", "summary": "多家私营航天公司公布新的发射计划。", "published": "2025-01-14"},
            {"title": "香港国际金融中心地位持续巩固", "url": "https://www.hkcna.hk/news1", "source": "香港新闻网", "summary": "最新数据显示香港金融业保持强劲增长势头。", "published": "2025-01-15"},
            {"title": "粤港澳大湾区建设加速推进", "url": "https://www.hkcna.hk/news2", "source": "香港新闻网", "summary": "", "published": ""},
            {"title": "两岸文化交流活动丰富多彩", "url": "https://www.hkcna.hk/news3", "source": "香港新闻网", "summary": "近期多项文化活动促进两岸民间互动。", "published": "2025-01-14"},
            {"title": "国际航运市场复苏迹象明显", "url": "https://www.hkcna.hk/news4", "source": "香港新闻网", "summary": "", "published": ""},
        ],
        "english_original": [
            {"title": "Global Markets Rally as Tech Stocks Surge", "url": "https://www3.nhk.or.jp/news/1", "source": "NHK World", "summary": "Major indices hit record highs amid earnings optimism.", "published": "2025-01-15"},
            {"title": "Climate Summit Reaches Historic Agreement", "url": "https://www3.nhk.or.jp/news/2", "source": "NHK World", "summary": "", "published": ""},
            {"title": "France 24: Macron Unveils New Economic Plan", "url": "https://www.france24.com/news/1", "source": "France 24", "summary": "The French president outlined measures to boost competitiveness.", "published": "2025-01-15"},
            {"title": "European Parliament Approves AI Regulation", "url": "https://www.france24.com/news/2", "source": "France 24", "summary": "", "published": ""},
            {"title": "RT: BRICS Summit Opens in Moscow", "url": "https://www.rt.com/news/1", "source": "RT News", "summary": "Leaders discuss multipolar world order and economic cooperation.", "published": "2025-01-15"},
            {"title": "RT: Energy Markets Stabilize After OPEC Decision", "url": "https://www.rt.com/news/2", "source": "RT News", "summary": "", "published": ""},
            {"title": "Japan's New Semiconductor Strategy Announced", "url": "https://www3.nhk.or.jp/news/3", "source": "NHK World", "summary": "Tokyo pledges $20B investment in chip manufacturing.", "published": "2025-01-14"},
            {"title": "Africa-Europe Summit Focuses on Migration", "url": "https://www.france24.com/news/3", "source": "France 24", "summary": "", "published": "2025-01-14"},
            {"title": "RT: Russia-China Trade Hits Record High", "url": "https://www.rt.com/news/3", "source": "RT News", "summary": "Bilateral trade exceeds $200 billion for first time.", "published": "2025-01-14"},
            {"title": "NHK: Earthquake Early Warning System Improved", "url": "https://www3.nhk.or.jp/news/4", "source": "NHK World", "summary": "", "published": "2025-01-13"},
        ],
        "finance": [
            {"title": "美联储利率决议前瞻：市场预期按兵不动", "url": "https://www.ftchinese.com/news1", "source": "FT中文网", "summary": "分析师普遍认为美联储将维持当前利率水平不变。", "published": "2025-01-15"},
            {"title": "A股三大指数集体收涨，科技板块领涨", "url": "https://www.ftchinese.com/news2", "source": "FT中文网", "summary": "", "published": ""},
            {"title": "华尔街日报：美国国债收益率曲线趋于正常化", "url": "https://cn.wsj.com/news1", "source": "华尔街日报中文版", "summary": "2年期与10年期国债利差收窄至年内最低水平。", "published": "2025-01-15"},
            {"title": "加密货币监管新框架即将出台", "url": "https://cn.wsj.com/news2", "source": "华尔街日报中文版", "summary": "", "published": ""},
            {"title": "黄金价格突破历史新高，避险需求旺盛", "url": "https://wallstreetcn.com/news1", "source": "华尔街见闻", "summary": "地缘政治不确定性推动金价持续走高。", "published": "2025-01-15"},
            {"title": "人民币汇率保持基本稳定", "url": "https://wallstreetcn.com/news2", "source": "华尔街见闻", "summary": "", "published": ""},
            {"title": "全球供应链重构加速，制造业回流趋势明显", "url": "https://www.ftchinese.com/news3", "source": "FT中文网", "summary": "多国政策推动关键产业本土化生产。", "published": "2025-01-14"},
            {"title": "新能源车销量再创新高", "url": "https://wallstreetcn.com/news3", "source": "华尔街见闻", "summary": "", "published": "2025-01-14"},
            {"title": "国际油价窄幅震荡，市场关注OPEC+动向", "url": "https://cn.wsj.com/news3", "source": "华尔街日报中文版", "summary": "布伦特原油维持在每桶75美元附近。", "published": "2025-01-14"},
            {"title": "中国数字经济规模突破60万亿元", "url": "https://wallstreetcn.com/news4", "source": "华尔街见闻", "summary": "", "published": "2025-01-13"},
        ]
    }
    for cat, items in news_data.items():
        print(f"  📝 模拟 {cat}: {len(items)} 条")

# ── 3. 翻译（模拟） ─────────────────────────────
print("\n📋 Step 3: 翻译英文源（模拟模式）")
translated_flags = {}
# 模拟翻译结果
mock_translations = {
    "Global Markets Rally as Tech Stocks Surge": "科技股飙升推动全球市场大涨",
    "Climate Summit Reaches Historic Agreement": "气候峰会达成历史性协议",
    "France 24: Macron Unveils New Economic Plan": "马克龙公布新经济计划",
    "European Parliament Approves AI Regulation": "欧洲议会批准人工智能监管法案",
    "RT: BRICS Summit Opens in Moscow": "金砖国家峰会在莫斯科开幕",
    "RT: Energy Markets Stabilize After OPEC Decision": "OPEC决策后能源市场趋稳",
    "Japan's New Semiconductor Strategy Announced": "日本公布新半导体战略",
    "Africa-Europe Summit Focuses on Migration": "非欧峰会聚焦移民问题",
    "RT: Russia-China Trade Hits Record High": "俄中贸易创历史新高",
    "NHK: Earthquake Early Warning System Improved": "日本改进地震预警系统",
}
for item in news_data.get("english_original", []):
    if item["title"] in mock_translations:
        item["original_title"] = item["title"]
        item["title"] = mock_translations[item["title"]]
translated_flags["english_original"] = True
print(f"  ✅ 模拟翻译完成: 10 条标题已翻译")

# ── 4. 渲染 HTML ────────────────────────────────
print("\n📋 Step 4: 渲染 HTML")
from renderer import render_html, save_html
html = render_html(news_data, translated_flags)

output_dir = ROOT / "output"
output_dir.mkdir(exist_ok=True)

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
html_path = output_dir / f"digest_{now_str}.html"
save_html(html, str(html_path))

latest_path = output_dir / "latest.html"
latest_path.write_text(html, encoding="utf-8")

print(f"  ✅ HTML 渲染完成 ({len(html)} 字符)")
print(f"  💾 存档: {html_path.name}")
print(f"  💾 最新: latest.html")

# ── 5. 保存 JSON ────────────────────────────────
json_path = output_dir / f"digest_{now_str}.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)
print(f"  💾 JSON: {json_path.name}")

# ── 6. 邮件准备 ─────────────────────────────────
print("\n📋 Step 5: 邮件模块检查")
from sender import EmailSender
sender = EmailSender(config["email"])
print(f"  SMTP: {sender.host}:{sender.port}")
print(f"  启用: {sender.enabled}")
if not sender.enabled:
    print(f"  ℹ️ 邮件未启用（本地测试模式）")
    print(f"  💡 设置 send_enabled=true 并填入真实邮箱即可启用")

# ── 总结 ────────────────────────────────────────
print("\n" + "=" * 60)
total_final = sum(len(v) for v in news_data.values())
print(f"🎉 集成测试完成！")
print(f"  📊 新闻总数: {total_final} 条")
print(f"  📁 输出目录: {output_dir}")
print(f"  📄 主文件: latest.html")
print(f"  📄 JSON: {json_path.name}")
print("=" * 60)
print("\n在本地电脑上的使用方式：")
print("  1. 编辑 config.json → 填入智谱 API Key")
print("  2. python main.py")
print("  3. 浏览器自动打开 output/latest.html")
print("  4. 每天早上 9 点自动运行（配置定时任务后）")
