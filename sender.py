import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_email(html_content, date_str):
    api_key = os.getenv("RESEND_API_KEY")
    to_email = os.getenv("TO_EMAIL")

    if not api_key:
        raise ValueError("❌ 未配置 RESEND_API_KEY")
    if not to_email:
        raise ValueError("❌ 未配置 TO_EMAIL")

    # 未验证域名时只能用这个发件地址
    from_addr = "每日新闻速递 <onboarding@resend.dev>"

    payload = {
        "from": from_addr,
        "to": [to_email],
        "subject": f"📰 每日新闻速递 · {date_str}",
        "html": html_content,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        "https://api.resend.com/emails",
        json=payload,
        headers=headers,
        timeout=30
    )

    # 让错误暴露出来，不要吞掉
    if resp.status_code >= 400:
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        raise RuntimeError(f"Resend API 错误 {resp.status_code}: {err}")

    data = resp.json()
    print(f"  ✅ 邮件已通过 Resend 发送至 {to_email}（ID: {data.get('id', 'unknown')}）")