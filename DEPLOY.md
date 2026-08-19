# 🚀 部署指南

## 一、准备工作

### 1. 智谱 AI（免费翻译）
1. 访问 https://open.bigmodel.cn/ 注册账号
2. 进入控制台 → API Keys → 创建新 Key
3. 免费额度：`glm-4-flash` 模型有免费额度，足够每天翻译 30 条新闻

### 2. 邮箱（发送邮件）
推荐方案：
- **Gmail**：开启两步验证 → 创建"应用专用密码" → 用这个密码作为 `SMTP_PASS`
- **QQ邮箱**：设置 → 账户 → 开启SMTP → 生成授权码
- **163邮箱**：设置 → POP3/SMTP → 开启 → 设置授权码

SMTP 常见配置：
| 邮箱 | SMTP_HOST | SMTP_PORT |
|---|---|---|
| Gmail | smtp.gmail.com | 587 |
| QQ邮箱 | smtp.qq.com | 587 |
| 163邮箱 | smtp.163.com | 587 |

## 二、部署到 GitHub

### 1. 创建仓库
```bash
# 在 GitHub 上创建新仓库，比如 news-digest
# 然后推送代码
cd news_digest
git init
git add .
git commit -m "init: daily news digest"
git remote add origin https://github.com/你的用户名/news-digest.git
git push -u origin main
```

### 2. 配置 Secrets
进入仓库 → Settings → Secrets and variables → Actions → New repository secret

需要添加以下 5 个 Secrets：

| Secret 名称 | 值 |
|---|---|
| `ZHIPU_API_KEY` | 智谱AI的API Key |
| `SMTP_HOST` | 如 smtp.gmail.com |
| `SMTP_PORT` | 如 587 |
| `SMTP_USER` | 你的邮箱地址 |
| `SMTP_PASS` | 邮箱应用密码/授权码 |
| `TO_EMAIL` | 接收邮件的地址 |

### 3. 触发方式
- **自动**：每天北京时间 09:00 自动运行
- **手动**：进入 Actions 标签页 → 选择 "每日新闻速递" → Run workflow

## 三、验证

1. 推送代码后，进入 Actions 看首次运行日志
2. 检查邮箱是否收到邮件
3. 如果某个新闻源总是 0 条，查看日志调整选择器

## 四、常见问题

**Q: 邮件收到但英文没翻译？**
A: 检查 `ZHIPU_API_KEY` 是否正确设置，免费额度是否用完

**Q: 某个新闻源抓不到内容？**
A: 网站结构可能更新，需要更新 fetcher.py 中的选择器。查看 Actions 日志里的 HTML 结构

**Q: 想加更多新闻源？**
A: 在 fetcher.py 中参照现有格式添加新函数，并注册到 `SOURCES` 列表

**Q: 想改发送时间？**
A: 修改 `.github/workflows/daily.yml` 中的 cron 表达式。注意是 UTC 时间：
- 北京时间 08:00 = UTC 00:00 → `0 0 * * *`
- 北京时间 09:00 = UTC 01:00 → `0 1 * * *`
- 北京时间 21:00 = UTC 13:00 → `0 13 * * *`

## 五、文件结构

```
news_digest/
├── .github/workflows/daily.yml   # GitHub Actions 配置
├── fetcher.py                     # 新闻抓取（9个新闻源）
├── translator.py                  # 智谱AI翻译
├── renderer.py                    # HTML邮件渲染
├── sender.py                      # SMTP邮件发送
├── main.py                        # 主入口
├── test_mock.py                   # 离线测试
├── test_rss_parser.py            # RSS解析测试
├── requirements.txt               # Python依赖
├── config.example.json           # 配置模板
└── DEPLOY.md                      # 本文档
```
