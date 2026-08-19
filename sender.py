"""
邮件发送模块
通过 SMTP 发送 HTML 邮件
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email(html_body: str, subject: str = "") -> bool:
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    to_addr = os.environ.get("TO_EMAIL", "")

    if not smtp_user or not smtp_pass or not to_addr:
        print("[邮件] 缺少 SMTP 配置，跳过发送")
        return False

    if not subject:
        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"🗞️ 每日新闻速递 · {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"每日新闻 <{smtp_user}>"
    msg["To"] = to_addr

    html_part = MIMEText(html_body, "html", "utf-8")
    msg.attach(html_part)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_addr, msg.as_string())
        print(f"[邮件] 已发送至 {to_addr}")
        return True
    except Exception as e:
        print(f"[邮件] 发送失败: {e}")
        return False
