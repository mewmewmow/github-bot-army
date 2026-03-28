"""
📬 Multi-Channel Notification Module v2.0
Supports: Email (SMTP), Telegram (free bot), Discord (webhook), Slack (webhook)
All bots import this for unified notifications.
Enhanced with rate limiting and retry logic.
"""
import os
import json
import smtplib
import urllib.request
import time
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_config() -> Dict[str, str]:
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
        # Slack (NEW)
        "slack_webhook": os.environ.get("SLACK_WEBHOOK_URL", ""),
    }


def retry_request(url: str, data: bytes, headers: Dict, max_retries: int = 3) -> Optional[str]:
    """Make HTTP request with retry logic."""
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode()
        except socket.timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except urllib.error.HTTPError as e:
            logger.warning(f"HTTP error {e.code} on attempt {attempt + 1}")
            if e.code == 429 and attempt < max_retries - 1:  # Too Many Requests
                time.sleep(10 * (attempt + 1))
        except Exception as e:
            logger.error(f"Request error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None


def send_email(subject: str, body: str, is_html: bool = True) -> str:
    """Send email notification with retry logic."""
    cfg = get_config()
    
    required = ["smtp_host", "smtp_user", "smtp_pass", "email_to"]
    if not all(cfg.get(k) for k in required):
        return "⏭️ Not configured"
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🤖 {subject}"
        msg["From"] = cfg["email_from"] or cfg["smtp_user"]
        msg["To"] = cfg["email_to"]
        
        if is_html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=30) as s:
            s.starttls()
            s.login(cfg["smtp_user"], cfg["smtp_pass"])
            s.send_message(msg)
        
        logger.info(f"📧 Email sent: {subject}")
        return "✅ Sent"
    
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Email auth error: {e}")
        return f"❌ Auth failed"
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error: {e}")
        return f"❌ {str(e)[:50]}"
    except Exception as e:
        logger.error(f"❌ Email error: {e}")
        return f"❌ {str(e)[:50]}"


def send_telegram(subject: str, body: str, is_html: bool = True) -> str:
    """Send Telegram notification with retry logic."""
    cfg = get_config()
    
    if not cfg.get("telegram_token") or not cfg.get("telegram_chat_id"):
        return "⏭️ Not configured"
    
    try:
        # Strip HTML for Telegram plain text
        text = f"🤖 **{subject}**\n\n{body}"
        if is_html:
            import re
            text = re.sub(r'<[^>]+>', '', text)  # Strip HTML tags
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        
        # Truncate if too long (Telegram limit 4096)
        if len(text) > 4000:
            text = text[:3990] + "\n\n... (truncated)"
        
        url = f"https://api.telegram.org/bot{cfg['telegram_token']}/sendMessage"
        data = json.dumps({
            "chat_id": cfg["telegram_chat_id"],
            "text": text,
            "parse_mode": "Markdown"
        }).encode()
        
        headers = {"Content-Type": "application/json"}
        result = retry_request(url, data, headers)
        
        if result:
            logger.info(f"📱 Telegram sent: {subject}")
            return "✅ Sent"
        return "❌ Failed after retries"
    
    except Exception as e:
        logger.error(f"❌ Telegram error: {e}")
        return f"❌ {str(e)[:50]}"


def send_discord(subject: str, body: str, is_html: bool = True) -> str:
    """Send Discord webhook notification."""
    cfg = get_config()
    
    if not cfg.get("discord_webhook"):
        return "⏭️ Not configured"
    
    try:
        # Strip HTML for Discord
        if is_html:
            import re
            body = re.sub(r'<[^>]+>', '', body)
            body = body.replace('&nbsp;', ' ').replace('&amp;', '&')
        
        # Truncate if too long (Discord embed limit 2000)
        if len(body) > 2000:
            body = body[:1990] + "..."
        
        embed = {
            "embeds": [{
                "title": f"🤖 {subject}",
                "description": body,
                "color": 3447003,  # Blue
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "footer": {"text": "GitHub Bot Army v2.0"}
            }]
        }
        
        data = json.dumps(embed).encode()
        headers = {"Content-Type": "application/json"}
        result = retry_request(cfg["discord_webhook"], data, headers)
        
        if result:
            logger.info(f"💬 Discord sent: {subject}")
            return "✅ Sent"
        return "❌ Failed after retries"
    
    except Exception as e:
        logger.error(f"❌ Discord error: {e}")
        return f"❌ {str(e)[:50]}"


def send_slack(subject: str, body: str, is_html: bool = True) -> str:
    """Send Slack webhook notification (NEW)."""
    cfg = get_config()
    
    if not cfg.get("slack_webhook"):
        return "⏭️ Not configured (add SLACK_WEBHOOK_URL)"
    
    try:
        # Strip HTML for Slack
        if is_html:
            import re
            body = re.sub(r'<[^>]+>', '', body)
            body = body.replace('&nbsp;', ' ').replace('&amp;', '&')
        
        # Truncate if too long (Slack max 3000)
        if len(body) > 3000:
            body = body[:2990] + "..."
        
        payload = {
            "text": f"🤖 *{subject}*",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"🤖 {subject}"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": body}
                }
            ]
        }
        
        data = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"}
        result = retry_request(cfg["slack_webhook"], data, headers)
        
        if result:
            logger.info(f"📎 Slack sent: {subject}")
            return "✅ Sent"
        return "❌ Failed after retries"
    
    except Exception as e:
        logger.error(f"❌ Slack error: {e}")
        return f"❌ {str(e)[:50]}"


def notify(subject: str, body: str, is_html: bool = True, channels: list = None) -> Dict[str, str]:
    """
    Send notification via ALL configured channels.
    Returns dict with results per channel.
    
    Args:
        subject: Notification title
        body: Notification body content
        is_html: Whether body contains HTML
        channels: Optional list of specific channels ['email', 'telegram', 'discord', 'slack']
                 If None, sends to all configured channels.
    """
    results = {}
    
    # Default: send to all configured channels
    target_channels = channels or ["email", "telegram", "discord", "slack"]
    
    if "email" in target_channels:
        results["email"] = send_email(subject, body, is_html)
    
    if "telegram" in target_channels:
        results["telegram"] = send_telegram(subject, body, is_html)
    
    if "discord" in target_channels:
        results["discord"] = send_discord(subject, body, is_html)
    
    if "slack" in target_channels:
        results["slack"] = send_slack(subject, body, is_html)
    
    # Summary
    success = sum(1 for v in results.values() if v.startswith("✅"))
    total = len(results)
    results["_summary"] = f"{success}/{total} channels succeeded"
    
    return results


def format_html_report(title: str, emoji: str, sections: Dict[str, str], 
                        accent_color: str = "#58a6ff") -> str:
    """Format a beautiful HTML email report with modern styling."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    html = f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#0d1117;color:#c9d1d9">
    <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;padding:24px">
        <h1 style="color:{accent_color};margin-top:0">{emoji} {title}</h1>
        <p style="color:#8b949e;font-size:14px">📅 {timestamp}</p>
        <hr style="border:none;border-top:1px solid #30363d">"""
    
    for section_title, content in sections.items():
        # Convert newlines to <br> for proper rendering
        content_html = content.replace('\n', '<br>')
        html += f"""
        <h2 style="color:#f0f6fc;font-size:16px;margin-top:24px">{section_title}</h2>
        <div style="background:#0d1117;border-radius:6px;padding:12px;font-family:monospace;font-size:13px;line-height:1.6;white-space:pre-wrap;overflow-x:auto">{content_html}</div>"""
    
    html += f"""
        <hr style="border:none;border-top:1px solid #30363d;margin-top:24px">
        <p style="color:#8b949e;font-size:12px;text-align:center">
            🤖 Generated by <strong>GitHub Bot Army v2.0</strong><br>
            <a href="https://github.com/mewmewmow/github-bot-army" style="color:{accent_color}">View on GitHub</a>
        </p>
    </div></body></html>"""
    return html


def format_health_card(stats: Dict[str, Any]) -> str:
    """Format a health score card for notifications."""
    health = stats.get("health", 0)
    emoji = "🟢" if health >= 80 else "🟡" if health >= 60 else "🔴"
    
    return f"""
{emoji} Health: {health}%
⭐ Stars: {stats.get("stars", 0)}
🍴 Forks: {stats.get("forks", 0)}
📁 Private: {stats.get("is_private", False)}
🔄 Updated: {stats.get("updated_at", "Unknown")}"""


def send_daily_summary(bot_results: Dict[str, Dict], channels: list = None) -> Dict[str, str]:
    """
    Send a consolidated daily summary from all bots.
    
    Args:
        bot_results: {"bot-name": {"status": "...", "data": {...}}, ...}
        channels: Optional list of specific channels
    
    Returns:
        Dict with channel results
    """
    summary_lines = []
    total_issues = 0
    total_fixes = 0
    bots_running = 0
    
    bot_emojis = {
        "repo-doctor": "🔧",
        "security-sentinel": "🛡️",
        "api-key-hunter": "🔑",
        "analytics": "📊",
        "update-bot": "🔄",
        "web-scraper": "🕷️",
        "bot-coordinator": "🧠",
        "deploy-bot": "🚀",
        "agent-builder": "🧬",
    }
    
    for bot_name, result in bot_results.items():
        emoji = bot_emojis.get(bot_name, "🤖")
        status = result.get("status", "unknown")
        summary_lines.append(f"{emoji} {bot_name}: {status}")
        
        if "issues" in result.get("data", {}):
            total_issues += len(result["data"]["issues"])
        if "fixes" in result.get("data", {}):
            total_fixes += len(result["data"]["fixes"])
        if status != "error":
            bots_running += 1
    
    summary = "\n".join(summary_lines)
    
    subject = f"Daily Report — {total_fixes} fixes, {total_issues} issues, {bots_running} bots active"
    
    sections = {
        "📊 Summary": summary,
        "📈 Totals": f"🔧 Fixes Applied: {total_fixes}\n⚠️ Issues Found: {total_issues}\n🤖 Bots Running: {bots_running}",
    }
    
    html = format_html_report("Daily Bot Army Report", "🤖", sections)
    
    return notify(subject, html, channels=channels)


def send_alert(alert_type: str, message: str, severity: str = "warning", 
               channels: list = None) -> Dict[str, str]:
    """
    Send an urgent alert notification.
    
    Args:
        alert_type: Type of alert (e.g., "security", "failure", "deployment")
        message: Alert message
        severity: "info", "warning", "error", "critical"
        channels: Optional list of specific channels
    """
    severity_emojis = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🚨"
    }
    
    emoji = severity_emojis.get(severity, "📢")
    subject = f"{emoji} {alert_type.title()} Alert"
    
    html = format_html_report(
        f"{alert_type.title()} Alert",
        emoji,
        {
            "🔍 Alert Type": alert_type,
            "📝 Message": message,
            "⚡ Severity": severity,
            "🕐 Time": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        },
        accent_color="#ff6b6b" if severity in ["error", "critical"] else "#f0ad4e"
    )
    
    # Always send alerts immediately (no batching)
    return notify(subject, html, channels=channels)


# Export all functions
__all__ = [
    "get_config",
    "notify",
    "send_email",
    "send_telegram",
    "send_discord",
    "send_slack",
    "format_html_report",
    "format_health_card",
    "send_daily_summary",
    "send_alert",
]