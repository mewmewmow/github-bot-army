"""
🐙 GitHub Helper Module — Shared utilities for all bots
"""
import os
import base64
import json
from github import Github


def get_client() -> Github:
    """Get authenticated GitHub client."""
    token = os.environ.get("GH_PAT", "")
    if not token:
        raise ValueError("GH_PAT not set")
    return Github(token)


def get_user():
    """Get authenticated user."""
    return get_client().get_user()


def get_all_repos(include_forks=False):
    """Get all repos for the authenticated user."""
    user = get_user()
    repos = []
    for repo in user.get_repos():
        if not include_forks and repo.fork:
            continue
        repos.append(repo)
    return repos


def repo_has_file(repo, filename):
    """Check if repo has a specific file."""
    try:
        repo.get_contents(filename)
        return True
    except:
        return False


def get_file_content(repo, filename):
    """Get file content from repo."""
    try:
        content = repo.get_contents(filename)
        return base64.b64decode(content.content).decode("utf-8", errors="ignore")
    except:
        return None


def repo_health_score(repo):
    """Calculate health score (0-100) for a repo."""
    score = 0
    checks = 0
    
    # Description (20 pts)
    checks += 20
    if repo.description:
        score += 20
    
    # Topics (15 pts)
    checks += 15
    if repo.get_topics():
        score += 15
    
    # README (20 pts)
    checks += 20
    if repo_has_file(repo, "README.md"):
        score += 20
    
    # LICENSE (15 pts)
    checks += 15
    if repo_has_file(repo, "LICENSE"):
        score += 15
    
    # .gitignore (10 pts)
    checks += 10
    if repo_has_file(repo, ".gitignore"):
        score += 10
    
    # .env.example (10 pts)
    checks += 10
    if repo_has_file(repo, ".env.example"):
        score += 10
    
    # CI/CD (10 pts)
    checks += 10
    if repo_has_file(repo, ".github/workflows") or repo_has_file(repo, ".github/workflows/ci.yml"):
        score += 10
    
    return round((score / checks) * 100) if checks > 0 else 0


def smart_description(repo):
    """Generate a smart description for a repo based on its contents."""
    lang = repo.language or "Project"
    name = repo.name.replace("-", " ").replace("_", " ").title()
    
    descriptions = {
        "Python": f"{name} — Python project",
        "JavaScript": f"{name} — JavaScript/Node.js project",
        "TypeScript": f"{name} — TypeScript project",
        "HTML": f"{name} — Web project",
        "Go": f"{name} — Go project",
        "Rust": f"{name} — Rust project",
        "Java": f"{name} — Java project",
    }
    
    return descriptions.get(lang, f"{name} project")


def smart_topics(repo):
    """Generate smart topics for a repo."""
    topics = []
    lang = repo.language
    
    lang_topics = {
        "Python": ["python"],
        "JavaScript": ["javascript", "nodejs"],
        "TypeScript": ["typescript"],
        "HTML": ["html", "css", "web"],
        "Go": ["golang"],
        "Rust": ["rust"],
        "Java": ["java"],
    }
    
    if lang and lang in lang_topics:
        topics.extend(lang_topics[lang])
    
    # Check for common frameworks
    content = get_file_content(repo, "package.json") or ""
    if '"next"' in content:
        topics.append("nextjs")
    if '"react"' in content:
        topics.append("react")
    if '"express"' in content:
        topics.append("express")
    if '"tailwindcss"' in content:
        topics.append("tailwindcss")
    
    content = get_file_content(repo, "requirements.txt") or ""
    if "fastapi" in content.lower():
        topics.append("fastapi")
    if "django" in content.lower():
        topics.append("django")
    if "flask" in content.lower():
        topics.append("flask")
    
    return topics or ["project"]
