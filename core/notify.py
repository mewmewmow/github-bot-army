"""
📬 GitHub Bot Army - Unified Notification Module v2.1
Shared by all workflows - handles Email, Telegram, Discord, Slack
"""
import os
import json
import smtplib
import urllib.request
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional


def get_config() -> Dict[str, str]:
    """Get all notification configs from environment."""
    return {
        "smtp_host": os.environ.get("SMTP_HOST", ""),
        "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
        "smtp_user": os.environ.get("SMTP_USER", ""),
        "smtp_pass": os.environ.get("SMTP_PASS", ""),
        "email_from": os.environ.get("EMAIL_FROM", ""),
        "email_to": os.environ.get("EMAIL_TO", ""),
        "telegram_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
        "discord_webhook": os.environ.get("DISCORD_WEBHOOK_URL", ""),
        "slack_webhook": os.environ.get("SLACK_WEBHOOK_URL", ""),
    }


def send_email(subject: str, body: str, is_html: bool = True) -> str:
    cfg = get_config()
    if not all(cfg.get(k) for k in ["smtp_host", "smtp_user", "smtp_pass", "email_to"]):
        return "⏭️ Not configured"
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🤖 {subject}"
        msg["From"] = cfg["email_from"] or cfg["smtp_user"]
        msg["To"] = cfg["email_to"]
        msg.attach(MIMEText(body, "html") if is_html else MIMEText(body, "plain"))
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=30) as s:
            s.starttls()
            s.login(cfg["smtp_user"], cfg["smtp_pass"])
            s.send_message(msg)
        return "✅ Sent"
    except Exception as e:
        return f"❌ {str(e)[:50]}"


def send_telegram(subject: str, body: str, is_html: bool = True) -> str:
    cfg = get_config()
    if not cfg.get("telegram_token") or not cfg.get("telegram_chat_id"):
        return "⏭️ Not configured"
    try:
        text = f"🤖 **{subject}**\n\n{body if not is_html else re.sub(r'<[^>]+>', '', body)}"
        if len(text) > 4000:
            text = text[:3990] + "\n\n... (truncated)"
        url = f"https://api.telegram.org/bot{cfg['telegram_token']}/sendMessage"
        data = json.dumps({"chat_id": cfg["telegram_chat_id"], "text": text, "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        return "✅ Sent"
    except Exception as e:
        return f"❌ {str(e)[:50]}"


def send_discord(subject: str, body: str, is_html: bool = True) -> str:
    cfg = get_config()
    if not cfg.get("discord_webhook"):
        return "⏭️ Not configured"
    try:
        clean_body = re.sub(r'<[^>]+>', '', body) if is_html else body
        if len(clean_body) > 2000:
            clean_body = clean_body[:1990] + "..."
        embed = {"embeds": [{"title": f"🤖 {subject}", "description": clean_body, "color": 3447003, "timestamp": datetime.utcnow().isoformat() + "Z", "footer": {"text": "GitHub Bot Army v2.1"}}]}
        data = json.dumps(embed).encode()
        req = urllib.request.Request(cfg["discord_webhook"], data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        return "✅ Sent"
    except Exception as e:
        return f"❌ {str(e)[:50]}"


def send_slack(subject: str, body: str, is_html: bool = True) -> str:
    cfg = get_config()
    if not cfg.get("slack_webhook"):
        return "⏭️ Not configured"
    try:
        clean_body = re.sub(r'<[^>]+>', '', body) if is_html else body
        if len(clean_body) > 3000:
            clean_body = clean_body[:2990] + "..."
        payload = {"text": f"🤖 *{subject}*", "blocks": [{"type": "header", "text": {"type": "plain_text", "text": f"🤖 {subject}"}}, {"type": "section", "text": {"type": "mrkdwn", "text": clean_body}}]}
        data = json.dumps(payload).encode()
        req = urllib.request.Request(cfg["slack_webhook"], data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        return "✅ Sent"
    except Exception as e:
        return f"❌ {str(e)[:50]}"


def notify_all(subject: str, body: str, is_html: bool = True) -> Dict[str, str]:
    results = {
        "email": send_email(subject, body, is_html),
        "telegram": send_telegram(subject, body, is_html),
        "discord": send_discord(subject, body, is_html),
        "slack": send_slack(subject, body, is_html)
    }
    success = sum(1 for v in results.values() if v.startswith("✅"))
    results["_summary"] = f"{success}/4 channels"
    print(f"📬 Notifications: {results['_summary']}")
    return results