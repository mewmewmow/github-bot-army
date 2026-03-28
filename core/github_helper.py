"""
🐙 GitHub Helper Module — Shared utilities for all bots
Version 2.0 - Enhanced with error handling & rate limiting
"""
import os
import base64
import json
import time
import random
from github import Github
from typing import Optional, List, Dict, Any


class RateLimitHandler:
    """Handle GitHub API rate limits gracefully."""
    
    @staticmethod
    def wait_for_rate_limit(github: Github):
        """Wait if approaching rate limit."""
        rate = github.get_rate_limit()
        remaining = rate.core.remaining
        reset_time = rate.core.reset
        
        if remaining < 10:
            wait_time = (reset_time - time.time()) + 5
            if wait_time > 0:
                print(f"⏳ Rate limit low ({remaining}), waiting {wait_time:.0f}s...")
                time.sleep(min(wait_time, 60))  # Cap at 60s
    
    @staticmethod
    def retry_with_backoff(func, max_retries=3):
        """Retry function with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                    wait = (2 ** attempt) + random.random()
                    print(f"⏳ Rate limited, retrying in {wait:.1f}s...")
                    time.sleep(wait)
                else:
                    raise


def get_client() -> Github:
    """Get authenticated GitHub client with rate limit handling."""
    token = os.environ.get("GH_PAT", "")
    if not token:
        raise ValueError("GH_PAT not set")
    return Github(token)


def get_user():
    """Get authenticated user."""
    return get_client().get_user()


def get_all_repos(include_forks=False, max_retries=3):
    """Get all repos with retry logic."""
    user = get_user()
    repos = []
    
    for attempt in range(max_retries):
        try:
            for repo in user.get_repos():
                if not include_forks and repo.fork:
                    continue
                repos.append(repo)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                wait = (2 ** attempt) + random.random()
                print(f"⚠️ Error getting repos, retrying in {wait:.1f}s...")
                time.sleep(wait)
            else:
                raise
    
    return repos


def repo_has_file(repo, filename) -> bool:
    """Check if repo has a specific file."""
    try:
        repo.get_contents(filename)
        return True
    except:
        return False


def get_file_content(repo, filename) -> Optional[str]:
    """Get file content from repo."""
    try:
        content = repo.get_contents(filename)
        return base64.b64decode(content.content).decode("utf-8", errors="ignore")
    except:
        return None


def get_readme_content(repo) -> Optional[str]:
    """Get README content with proper encoding handling."""
    try:
        readme = repo.get_readme()
        return base64.b64decode(readme.content).decode("utf-8", errors="ignore")
    except:
        return None


def repo_health_score(repo) -> int:
    """Calculate health score (0-100) for a repo."""
    score = 0
    checks = 0
    
    # Description (15 pts)
    checks += 15
    if repo.description:
        score += 15
    
    # Topics (10 pts)
    checks += 10
    if repo.get_topics():
        score += 10
    
    # README (20 pts)
    checks += 20
    if repo_has_file(repo, "README.md"):
        score += 20
    
    # LICENSE (10 pts)
    checks += 10
    if repo_has_file(repo, "LICENSE"):
        score += 10
    
    # .gitignore (10 pts)
    checks += 10
    if repo_has_file(repo, ".gitignore"):
        score += 10
    
    # .env.example (10 pts)
    checks += 10
    if repo_has_file(repo, ".env.example"):
        score += 10
    
    # CI/CD (15 pts)
    checks += 15
    if repo_has_file(repo, ".github/workflows") or repo_has_file(repo, ".github/workflows/ci.yml"):
        score += 15
    
    return round((score / checks) * 100) if checks > 0 else 0


def smart_description(repo) -> str:
    """Generate a smart description for a repo based on its contents."""
    lang = repo.language or "Project"
    name = repo.name.replace("-", " ").replace("_", " ").title()
    
    descriptions = {
        "Python": f"{name} — Python project",
        "JavaScript": f"{name} — JavaScript/Node.js project",
        "TypeScript": f"{name} — TypeScript project",
        "HTML": f"{name} — Web project",
        "CSS": f"{name} — Web styles project",
        "Go": f"{name} — Go project",
        "Rust": f"{name} — Rust project",
        "Java": f"{name} — Java project",
        "C++": f"{name} — C++ project",
        "C#": f"{name} — C# project",
    }
    
    return descriptions.get(lang, f"{name} project")


def smart_topics(repo) -> List[str]:
    """Generate smart topics for a repo."""
    topics = []
    lang = repo.language
    
    lang_topics = {
        "Python": ["python", "python3"],
        "JavaScript": ["javascript", "nodejs", "node"],
        "TypeScript": ["typescript", "ts"],
        "HTML": ["html", "html5", "web"],
        "CSS": ["css", "css3", "styling"],
        "Go": ["golang", "go"],
        "Rust": ["rust", "rustlang"],
        "Java": ["java", "jvm"],
        "C++": ["cpp", "c-plus-plus"],
        "C#": ["csharp", "dotnet"],
    }
    
    if lang and lang in lang_topics:
        topics.extend(lang_topics[lang])
    
    # Check for common frameworks from package.json
    content = get_file_content(repo, "package.json") or ""
    if '"next"' in content:
        topics.append("nextjs")
    if '"react"' in content:
        topics.append("react")
    if '"express"' in content:
        topics.append("express")
    if '"vue"' in content:
        topics.append("vue")
    if '"tailwindcss"' in content:
        topics.append("tailwindcss")
    
    # Check Python frameworks from requirements.txt
    content = get_file_content(repo, "requirements.txt") or ""
    if "fastapi" in content.lower():
        topics.append("fastapi")
    if "django" in content.lower():
        topics.append("django")
    if "flask" in content.lower():
        topics.append("flask")
    if "pytest" in content.lower():
        topics.append("pytest")
    
    # Check for Go modules
    content = get_file_content(repo, "go.mod") or ""
    if content:
        topics.append("golang")
    
    return topics or ["project"]


def create_or_update_file(repo, path: str, content: str, message: str, sha: str = None) -> bool:
    """Create or update a file in the repo."""
    try:
        if sha:
            repo.update_file(path, message, content, sha)
        else:
            try:
                existing = repo.get_contents(path)
                repo.update_file(path, message, content, existing.sha)
            except:
                repo.create_file(path, message, content)
        return True
    except Exception as e:
        print(f"Error updating {path}: {e}")
        return False


def get_repo_stats(repo) -> Dict[str, Any]:
    """Get comprehensive stats for a repo."""
    return {
        "name": repo.name,
        "full_name": repo.full_name,
        "url": repo.html_url,
        "description": repo.description,
        "language": repo.language,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "watchers": repo.watchers_count,
        "topics": repo.get_topics(),
        "health": repo_health_score(repo),
        "is_private": repo.private,
        "is_fork": repo.fork,
        "created_at": repo.created_at.isoformat(),
        "updated_at": repo.updated_at.isoformat(),
        "has_readme": repo_has_file(repo, "README.md"),
        "has_license": repo_has_file(repo, "LICENSE"),
        "has_gitignore": repo_has_file(repo, ".gitignore"),
        "has_env_example": repo_has_file(repo, ".env.example"),
        "has_workflows": repo_has_file(repo, ".github/workflows"),
    }


def detect_code_issues(repo) -> List[Dict[str, str]]:
    """Detect common code issues in a repo."""
    issues = []
    
    # Check for hardcoded secrets in common files
    files_to_check = ["index.js", "app.js", "main.py", "config.js", "settings.py"]
    
    for filename in files_to_check:
        content = get_file_content(repo, filename)
        if content:
            # Check for potential API keys
            if "api_key" in content.lower() or "apikey" in content.lower():
                if "=" in content and not content.startswith("#"):
                    issues.append({
                        "file": filename,
                        "type": "potential_secret",
                        "message": "Possible hardcoded API key detected"
                    })
    
    # Check for missing .gitignore
    if not repo_has_file(repo, ".gitignore"):
        issues.append({
            "file": ".gitignore",
            "type": "missing",
            "message": "Missing .gitignore file"
        })
    
    # Check for missing README in main repos
    if not repo_has_file(repo, "README.md") and not repo.private:
        issues.append({
            "file": "README.md",
            "type": "missing",
            "message": "Missing README.md - hurts discoverability"
        })
    
    return issues


# Export everything
__all__ = [
    "RateLimitHandler",
    "get_client",
    "get_user", 
    "get_all_repos",
    "repo_has_file",
    "get_file_content",
    "get_readme_content",
    "repo_health_score",
    "smart_description",
    "smart_topics",
    "create_or_update_file",
    "get_repo_stats",
    "detect_code_issues",
]