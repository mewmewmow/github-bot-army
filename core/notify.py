"""
📬 Multi-Channel Notification Module
Supports: Email (SMTP), Telegram (free bot), Discord (free webhook)
All bots import this for unified notifications.
"""
import os
import json
import smtplib
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def get_config():
    """Get all notification configs from environment."""
    return {
        # Email
        "smtp_host": os.environ.get("SMTP_HOST", ""),
        "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
        "smtp_user": os.environ.get("SMTP_USER", ""),
        "smtp_pass": os.environ.get("SMTP_PASS", ""),
        "email_from": os.environ.get("EMAIL_FROM", ""),
        "email_to": os.environ.get("EMAIL_TO", ""),
        # Telegram
        "telegram_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
        # Discord
        "discord_webhook": os.environ.get("DISCORD_WEBHOOK_URL", ""),
    }


def notify(subject: str, body: str, is_html: bool = True) -> dict:
    """
    Send notification via ALL configured channels.
    Returns dict with results per channel.
    """
    cfg = get_config()
    results = {}
    
    # --- EMAIL ---
    if all([cfg["smtp_host"], cfg["smtp_user"], cfg["smtp_pass"], cfg["email_to"]]):
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🤖 {subject}"
            msg["From"] = cfg["email_from"] or cfg["smtp_user"]
            msg["To"] = cfg["email_to"]
            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as s:
                s.starttls()
                s.login(cfg["smtp_user"], cfg["smtp_pass"])
                s.send_message(msg)
            results["email"] = "✅ Sent"
            print(f"📧 Email sent: {subject}")
        except Exception as e:
            results["email"] = f"❌ {e}"
            print(f"❌ Email error: {e}")
    else:
        results["email"] = "⏭️ Not configured"
    
    # --- TELEGRAM ---
    if cfg["telegram_token"] and cfg["telegram_chat_id"]:
        try:
            # Strip HTML for Telegram plain text
            text = f"🤖 **{subject}**\n\n{body}"
            if is_html:
                import re
                text = re.sub(r'<[^>]+>', '', text)  # Strip HTML tags
                text = text.replace('&nbsp;', ' ')
            
            # Truncate if too long (Telegram limit 4096)
            if len(text) > 4000:
                text = text[:3990] + "\n\n... (truncated)"
            
            url = f"https://api.telegram.org/bot{cfg['telegram_token']}/sendMessage"
            data = json.dumps({
                "chat_id": cfg["telegram_chat_id"],
                "text": text,
                "parse_mode": "Markdown"
            }).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=10)
            results["telegram"] = "✅ Sent"
            print(f"📱 Telegram sent: {subject}")
        except Exception as e:
            results["telegram"] = f"❌ {e}"
            print(f"❌ Telegram error: {e}")
    else:
        results["telegram"] = "⏭️ Not configured"
    
    # --- DISCORD ---
    if cfg["discord_webhook"]:
        try:
            # Discord embed
            embed = {
                "embeds": [{
                    "title": f"🤖 {subject}",
                    "description": body[:2000] if not is_html else "Report generated",
                    "color": 3447003,  # Blue
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "GitHub Bot Army"}
                }]
            }
            data = json.dumps(embed).encode()
            req = urllib.request.Request(cfg["discord_webhook"], data=data, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=10)
            results["discord"] = "✅ Sent"
            print(f"💬 Discord sent: {subject}")
        except Exception as e:
            results["discord"] = f"❌ {e}"
            print(f"❌ Discord error: {e}")
    else:
        results["discord"] = "⏭️ Not configured"
    
    return results


def format_html_report(title: str, emoji: str, sections: dict) -> str:
    """Format a beautiful HTML email report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#0d1117;color:#c9d1d9">
    <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:24px">
        <h1 style="color:#58a6ff;margin-top:0">{emoji} {title}</h1>
        <p style="color:#8b949e;font-size:14px">📅 {timestamp}</p>
        <hr style="border:none;border-top:1px solid #30363d">"""
    
    for section_title, content in sections.items():
        html += f"""
        <h2 style="color:#f0f6fc;font-size:16px">{section_title}</h2>
        <div style="background:#0d1117;border-radius:6px;padding:12px;font-family:monospace;font-size:13px;line-height:1.6;white-space:pre-wrap">{content}</div>"""
    
    html += """
        <hr style="border:none;border-top:1px solid #30363d;margin-top:20px">
        <p style="color:#8b949e;font-size:12px;text-align:center">
            🤖 Generated by GitHub Bot Army<br>
            <a href="https://github.com/mewmewmow/github-bot-army" style="color:#58a6ff">View on GitHub</a>
        </p>
    </div></body></html>"""
    return html


def send_daily_summary(bot_results: dict):
    """
    Send a consolidated daily summary from all bots.
    bot_results = {"repo-doctor": {"status": "...", "data": {...}}, ...}
    """
    summary_lines = []
    total_issues = 0
    total_fixes = 0
    
    for bot_name, result in bot_results.items():
        emoji = {"repo-doctor":"🔧","security-sentinel":"🛡️","api-key-hunter":"🔑","analytics":"📊","update-bot":"🔄","web-scraper":"🕷️"}.get(bot_name, "🤖")
        summary_lines.append(f"{emoji} {bot_name}: {result.get('status','unknown')}")
        if 'issues' in result.get('data', {}):
            total_issues += len(result['data']['issues'])
        if 'fixes' in result.get('data', {}):
            total_fixes += len(result['data']['fixes'])
    
    summary = "\n".join(summary_lines)
    subject = f"Daily Report — {total_fixes} fixes, {total_issues} issues across all bots"
    
    html = format_html_report("Daily Bot Army Report", "🤖", {
        "📊 Summary": summary,
        "📈 Totals": f"🔧 Fixes Applied: {total_fixes}\n⚠️ Issues Found: {total_issues}",
    })
    
    notify(subject, html)
