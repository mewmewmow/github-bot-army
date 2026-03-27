#!/bin/bash
# 🤖 GitHub Bot Army — Setup Script
# Run this once to set up everything

set -e

echo "🤖 GitHub Bot Army — Setup"
echo "=========================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI not found. Install: https://cli.github.com${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Check auth
echo -e "\n${YELLOW}Checking GitHub auth...${NC}"
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}🔑 Please authenticate with GitHub:${NC}"
    gh auth login
fi
echo -e "${GREEN}✅ GitHub authenticated${NC}"

# Create the repo
echo -e "\n${YELLOW}Creating GitHub Bot Army repo...${NC}"
REPO_NAME="github-bot-army"

if gh repo view "$REPO_NAME" &> /dev/null; then
    echo -e "${YELLOW}⚠️ Repo already exists, skipping creation${NC}"
else
    gh repo create "$REPO_NAME" --public --description "🤖 Autonomous GitHub automation bot ecosystem — 10 bots that maintain, secure, deploy, and enhance your GitHub 24/7"
    echo -e "${GREEN}✅ Repo created${NC}"
fi

# Push code
echo -e "\n${YELLOW}Pushing bot army code...${NC}"
cd github-bots
git init
git add .
git commit -m "🤖 Deploy GitHub Bot Army — 10 autonomous bots"
git branch -M main
git remote add origin "https://github.com/$(gh api user --jq '.login')/$REPO_NAME.git" 2>/dev/null || true
git push -u origin main --force
echo -e "${GREEN}✅ Code pushed${NC}"

# Set up secrets
echo -e "\n${YELLOW}Setting up secrets...${NC}"
echo -e "${YELLOW}You need to add these secrets to your repo:${NC}"
echo -e "  1. GH_PAT — GitHub Personal Access Token"
echo -e "  2. OPENROUTER_API_KEY — (optional) For AI features"
echo -e "\nGo to: https://github.com/$(gh api user --jq '.login')/$REPO_NAME/settings/secrets/actions"

echo -e "\n${GREEN}🎉 Setup complete! Your bot army is ready!${NC}"
echo -e "\nBots will activate on their first scheduled run."
echo -e "To trigger manually: Go to Actions tab → Select a bot → Run workflow"
