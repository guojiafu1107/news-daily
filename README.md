# 每日新闻速递 · 国内权威版

每天上午 9 点（或手动触发）抓取 **10 个国内可直连的权威新闻源**，汇总成卡片式 HTML 邮件发送。

## 特性

- 🇨🇳 **10 个国内权威信源**：新华社、人民日报、央视网、中国新闻网 + CGTN / 中国日报（英文）
- 📌 **每条新闻标注来源**（来源标签 + 分类着色）
- 🌐 **英文源自动翻译**：调用智谱 GLM-4-Flash，邮件中**原文 + 中文译文对照**显示
- 🚫 **中文源不翻译**，原样呈现
- ⚡ **轻量依赖**：仅 requests / beautifulsoup4 / lxml / python-dotenv（无 zhipuai SDK，无 sniffio/jieba）
- 🔁 RSS 双解析（RSS 2.0 + Atom）+ 自动重试

## 新闻源一览

| 分类 | 信源 | 语言 |
|------|------|------|
| 国际 | 新华网·国际 / 人民网·国际 / 央视网·国际 | 中文 |
| 时政 | 新华网·时政 / 人民网·要闻 / 央视网·国内 | 中文 |
| 财经 | 新华网·财经 / 中国新闻网·财经 | 中文 |
| 国际/综合 | CGTN·World / 中国日报·China Daily | 英文（译） |

## 快速开始

```bash
pip install -r requirements.txt
copy .env.example .env      # Windows（Mac/Linux 用 cp）
# 编辑 .env 填入 SMTP 邮箱与授权码；如需翻译英文则填 ZHIPU_API_KEY
python main.py
```

## 定时运行

- **Windows 任务计划程序**：触发器每天 09:00，操作启动 `run.bat`
- **Mac/Linux crontab**：`0 9 * * * cd /项目路径 && python3 main.py >> cron.log 2>&1`

## GitHub Actions

推送后自动按 `daily.yml` 每天北京时间 09:00 运行；需在仓库 Settings → Secrets 配置 `ZHIPU_API_KEY` 与 `SMTP_*`。
