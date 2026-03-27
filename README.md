# 🤖 GitHub Bot Army — 24/7 Autonomous Automation

> **10+ bots that maintain, secure, deploy, and enhance your GitHub — completely hands-free. Reports to Email, Telegram, and Discord.**

---

## 🤖 Your Bots (11 Total)

| # | Bot | What It Does | Schedule |
|---|-----|-------------|----------|
| 1 | 🔧 **Repo Doctor** | Auto-fixes repos (descriptions, topics, README, LICENSE, .gitignore) | Every 4h |
| 2 | 🛡️ **Security Sentinel** | Scans for exposed secrets, missing protection, vulnerabilities | Every 4h |
| 3 | 🔑 **API Key Hunter** | Finds free AI APIs, tests availability, maintains registry | Every 3h |
| 4 | 🕷️ **Web Scraper** | Scrapes trending repos, HackerNews, job opportunities | Every 6h |
| 5 | 🚀 **Deploy Bot** | Auto-deploys projects (Vercel/Netlify/GitHub Pages) | On push |
| 6 | 🧬 **Agent Builder** | Creates AI agent projects (Discord/Telegram bots, APIs) | Daily |
| 7 | 📊 **Analytics Bot** | Tracks stars, forks, health scores, language stats | Daily 8am |
| 8 | 🔄 **Update Bot** | Finds outdated dependencies, suggests updates | Daily 6am |
| 9 | 📦 **Project Generator** | Creates new projects from trending ideas | Weekly |
| 10 | 🏗️ **Scaffold Bot** | Scaffolds full-stack apps on demand | On demand |
| 11 | 📬 **Master Report** | **Daily consolidated report via Email + Telegram + Discord** | Daily 9am |
| 12 | ⚙️ **Bot Health Monitor** | Checks if all bots are running, alerts on failures | Daily noon |

---

## 📬 Notification Channels (All Free!)

| Channel | Cost | Setup Time | How |
|---------|------|-----------|-----|
| 📧 **Email** | Free (300-500/day) | 5 min | Gmail, Brevo, SendGrid, etc. |
| 📱 **Telegram** | **100% Free, Unlimited** | 2 min | Create bot via @BotFather |
| 💬 **Discord** | **100% Free, Unlimited** | 1 min | Server webhook |
| 🐙 **GitHub Issues** | 100% Free | 0 min | Auto-created for alerts |

### You'll Get:
- 📬 **Daily consolidated report** at 9am UTC
- 🛡️ **Instant security alerts** when secrets are exposed
- 🔧 **Fix summaries** when repos are auto-repaired
- 📊 **Weekly analytics** with health scores
- ⚙️ **Bot health alerts** if any bot fails

---

## 🚀 Setup (10 Minutes)

### Step 1: Create the Repo
```bash
# In terminal:
cd github-bot-army
git init && git add . && git commit -m "🤖 Deploy Bot Army"
gh repo create github-bot-army --public --source=. --push
```

### Step 2: Add Required Secrets
Go to **repo → Settings → Secrets and variables → Actions** and add:

| Secret | Required | How to Get |
|--------|----------|-----------|
| `GH_PAT` | ✅ | [github.com/settings/tokens](https://github.com/settings/tokens) — check `repo`, `workflow` |
| `SMTP_HOST` | ✅ | See free options below |
| `SMTP_PORT` | ✅ | Usually `587` |
| `SMTP_USER` | ✅ | Your SMTP email |
| `SMTP_PASS` | ✅ | SMTP password/app password |
| `EMAIL_FROM` | ✅ | Sender address |
| `EMAIL_TO` | ✅ | Your email |

### Step 3: Add Optional Channels (Recommended!)

| Secret | How to Get |
|--------|-----------|
| `TELEGRAM_BOT_TOKEN` | Open Telegram → @BotFather → `/newbot` → copy token |
| `TELEGRAM_CHAT_ID` | Message your bot → visit `https://api.telegram.org/botTOKEN/getUpdates` → find chat ID |
| `DISCORD_WEBHOOK_URL` | Discord → Server Settings → Integrations → Webhooks → Create → Copy URL |

### Step 4: Done! 🎉
Bots activate on their first scheduled run. You'll start receiving reports within hours.

---

## 📧 Free Email Options

| Service | Free Limit | Setup |
|---------|-----------|-------|
| **Gmail** | 500/day | Enable 2FA → [App Passwords](https://myaccount.google.com/apppasswords) |
| **Brevo** | 300/day | [brevo.com](https://brevo.com) — free SMTP |
| **SendGrid** | 100/day | [sendgrid.com](https://sendgrid.com) — free tier |
| **Mailgun** | 100/day | [mailgun.com](https://mailgun.com) — free tier |
| **Resend** | 100/day | [resend.com](https://resend.com) — developer-friendly |

---

## 📁 Structure

```
github-bot-army/
├── .github/workflows/
│   ├── repo-doctor.yml          # 🔧 Fix repos
│   ├── security-sentinel.yml    # 🛡️ Security scan
│   ├── api-key-hunter.yml       # 🔑 Find free APIs
│   ├── web-scraper.yml          # 🕷️ Scrape opportunities
│   ├── deploy-bot.yml           # 🚀 Auto-deploy
│   ├── agent-builder.yml        # 🧬 Create AI agents
│   ├── analytics-bot.yml        # 📊 Track stats
│   ├── update-bot.yml           # 🔄 Dependency updates
│   ├── project-generator.yml    # 📦 New projects
│   ├── scaffold-bot.yml         # 🏗️ Scaffold apps
│   ├── master-report.yml        # 📬 Daily consolidated report
│   └── bot-health.yml           # ⚙️ Monitor bot health
├── core/
│   └── notify.py                # Multi-channel notification module
├── config/
│   └── bots.yml                 # Bot configuration & schedules
├── data/                        # Generated reports (auto-committed)
├── scripts/
│   └── setup.sh                 # One-time setup script
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🔒 Security

- All secrets stored in GitHub Secrets (never in code)
- Bots use minimal required permissions
- All actions are logged in Actions tab
- No data leaves your GitHub ecosystem

---

## 📜 License

MIT — Use it, fork it, share it.

---

**Built by [mewmewmow](https://github.com/mewmewmow) 🤖**
