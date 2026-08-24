"""
test_run.py — 分步测试脚本，验证每个模块
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

print("=" * 60)
print("🧪 测试 1: 配置文件加载")
print("=" * 60)
try:
    with open(ROOT / "config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    print(f"  ✅ 配置加载成功")
    print(f"  📂 分类数: {len(config['sources'])}")
    for cat, sources in config["sources"].items():
        print(f"     {cat}: {len(sources)} 个源")
    print(f"  🔑 翻译模型: {config['translation']['model']}")
    print(f"  📧 邮件启用: {config['email']['send_enabled']}")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🧪 测试 2: 新闻抓取（仅 RSS，不翻译）")
print("=" * 60)
try:
    from fetcher import Fetcher
    fetcher = Fetcher(config)
    results = fetcher.fetch_all()

    total = 0
    for cat, items in results.items():
        print(f"\n  📂 {cat}: {len(items)} 条")
        for i, item in enumerate(items[:3], 1):
            print(f"     {i}. {item.title[:60]}")
            print(f"        🔗 {item.url[:80]}")
        if len(items) > 3:
            print(f"     ... 还有 {len(items)-3} 条")
        total += len(items)

    print(f"\n  📊 总计: {total} 条")
    if total == 0:
        print("  ⚠️ 全部为 0 条，可能是沙盒网络限制")
        print("  💡 在本地电脑运行通常不会有这个问题")
    else:
        print(f"  ✅ 抓取成功！")

except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🧪 测试 3: 翻译模块初始化（不实际调用API）")
print("=" * 60)
try:
    from translator import Translator
    # 用假 key 测试初始化逻辑
    t = Translator(api_key="test_key", model="glm-4-flash")
    print(f"  ✅ 翻译器初始化成功（Key 已设置）")
    print(f"  📁 缓存目录: {t.cache_dir}")
    # 测试缓存
    cached = t.translate("This is a test", target="zh")
    print(f"  🔤 测试翻译: 'This is a test' → '{cached}'")
    print(f"  📝 缓存条目数: {len(t.cache)}")
except Exception as e:
    print(f"  ❌ 失败: {e}")

print("\n" + "=" * 60)
print("🧪 测试 4: HTML 渲染")
print("=" * 60)
try:
    from renderer import render_html, save_html

    # 用模拟数据渲染
    mock_data = {
        "chinese_international": [
            {"title": "测试新闻标题一：国际局势最新动态", "url": "https://example.com/1", "source": "联合早报", "summary": "这是一条测试摘要内容", "published": "2025-01-15"},
            {"title": "测试新闻标题二：全球经济展望", "url": "https://example.com/2", "source": "环球网", "summary": "", "published": ""},
        ],
        "english_original": [
            {"title": "Global Markets Rally on Tech Earnings", "url": "https://example.com/3", "source": "NHK World", "summary": "", "published": ""},
        ],
        "finance": []
    }
    mock_flags = {"english_original": True}

    html = render_html(mock_data, mock_flags)
    save_html(html, str(ROOT / "output" / "test_preview.html"))
    print(f"  ✅ HTML 渲染成功 ({len(html)} 字符)")
    print(f"  💾 预览文件: {ROOT / 'output' / 'test_preview.html'}")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🧪 测试 5: 邮件模块（不实际发送）")
print("=" * 60)
try:
    from sender import EmailSender
    sender = EmailSender(config["email"])
    print(f"  ✅ 邮件发送器初始化")
    print(f"  📧 SMTP: {sender.host}:{sender.port}")
    print(f"  👤 发件人: {sender.user}")
    print(f"  📬 收件人: {sender.to_email}")
    print(f"  🔓 启用状态: {sender.enabled}")
    if not sender.enabled:
        print(f"  ℹ️ 邮件未启用（send_enabled=false），符合预期")
except Exception as e:
    print(f"  ❌ 失败: {e}")

print("\n" + "=" * 60)
print("✅ 所有测试完成！")
print("=" * 60)
print("\n在本地电脑上的使用步骤：")
print("  1. pip install -r requirements.txt")
print("  2. 编辑 config.json 填入智谱 API Key")
print("  3. python main.py")
print("  4. 浏览器自动打开 output/latest.html")
