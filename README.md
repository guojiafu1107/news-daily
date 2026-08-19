# 每日新闻聚合邮件系统

## 架构
GitHub Actions 定时触发 → Python 脚本抓取 7 个新闻源 → 智谱 GLM 翻译英文 → 渲染 HTML 邮件 → 通过 SMTP 发送

## 新闻源
- 联合早报 https://www.zaobao.com
- 环球网 https://world.huanqiu.com
- 香港新闻网 https://www.hkcna.hk
- NHK https://www3.nhk.or.jp/nhkworld/
- France 24 https://www.france24.com/en/
- RT https://www.rt.com
- FT 中文网 https://www.ftchinese.com
- 华尔街日报中文版 https://cn.wsj.com
- 华尔街见闻 https://wallstreetcn.com

## 文件结构
- main.py              入口
- fetcher.py           抓取各新闻源
- translator.py        智谱翻译
- renderer.py          渲染 HTML
- sender.py            发送邮件
- requirements.txt
- .github/workflows/daily.yml
- config.example.json  配置模板（不含真实密钥）
