#!/usr/bin/env python3
"""
llms.txt Generator — Creates and validates llms.txt files for AI crawler guidance.

The llms.txt standard helps AI crawlers understand site structure
and find the most important content.

Location: /llms.txt (root of domain)
Extended:  /llms-full.txt (detailed version)
"""

import sys
import json
import re
from urllib.parse import urljoin, urlparse
from typing import Protocol

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Required packages not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ---------------------------------------------------------------------------
# Validation (S — single responsibility)
# ---------------------------------------------------------------------------

class LlmsTxtValidator:
    """Validates format and content of an existing llms.txt."""

    def __init__(self, content: str):
        self._content = content
        self._lines = content.strip().split("\n")

    def validate(self) -> dict:
        has_title = bool(self._lines and self._lines[0].startswith("# "))
        has_desc = any(l.startswith("> ") for l in self._lines)
        sections = [l for l in self._lines if l.startswith("## ")]
        links = re.findall(r"- \[.+\]\(.+\)", self._content)

        issues: list[str] = []
        suggestions: list[str] = []

        if not has_title:
            issues.append("Missing title (should start with '# Site Name')")
        if not has_desc:
            issues.append("Missing description (use '> Brief description')")
        if not sections:
            issues.append("No sections found (use '## Section Name')")
        if not links:
            issues.append("No page links (use '- [Page Title](url): Description')")

        if len(links) < 5:
            suggestions.append("Consider adding more key pages (aim for 10-20)")
        if len(sections) < 2:
            suggestions.append("Add more sections to organize content types")
        if "contact" not in self._content.lower():
            suggestions.append("Add a Contact section with email and location")

        return {
            "has_title": has_title,
            "has_description": has_desc,
            "has_sections": bool(sections),
            "has_links": bool(links),
            "section_count": len(sections),
            "link_count": len(links),
            "format_valid": has_title and has_desc and bool(sections) and bool(links),
            "issues": issues,
            "suggestions": suggestions,
        }


# ---------------------------------------------------------------------------
# Fetcher abstraction
# ---------------------------------------------------------------------------

class Fetcher(Protocol):
    def get(self, url: str, timeout: int) -> requests.Response: ...


class DefaultFetcher:
    def get(self, url: str, timeout: int = 30) -> requests.Response:
        return requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)


# ---------------------------------------------------------------------------
# Validate remote llms.txt
# ---------------------------------------------------------------------------

def validate_llmstxt(url: str, fetcher: Fetcher | None = None) -> dict:
    """Check if llms.txt exists on the given domain and validate it."""
    fetcher = fetcher or DefaultFetcher()
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    llms_url = f"{base}/llms.txt"
    llms_full_url = f"{base}/llms-full.txt"

    result: dict = {
        "url": llms_url,
        "exists": False,
        "content": "",
        "full_version": {"url": llms_full_url, "exists": False},
    }

    try:
        resp = fetcher.get(llms_url, timeout=15)
        if resp.status_code == 200:
            result["exists"] = True
            result["content"] = resp.text
            result.update(LlmsTxtValidator(resp.text).validate())
        else:
            result["issues"] = [f"llms.txt returned status {resp.status_code}"]
    except Exception as e:
        result["issues"] = [f"Error fetching llms.txt: {e}"]

    try:
        resp = fetcher.get(llms_full_url, timeout=15)
        if resp.status_code == 200:
            result["full_version"]["exists"] = True
    except Exception:
        pass

    return result


# ---------------------------------------------------------------------------
# Page categorizer
# ---------------------------------------------------------------------------

CATEGORIES = {
    "Products & Services": ["/pricing", "/feature", "/product", "/solution", "/demo"],
    "Resources & Blog": ["/blog", "/article", "/resource", "/guide", "/learn", "/docs", "/documentation"],
    "Company": ["/about", "/team", "/career", "/contact", "/press", "/partner"],
    "Support": ["/help", "/support", "/faq", "/status"],
}


def _categorize_path(path: str) -> str:
    low = path.lower()
    for category, keywords in CATEGORIES.items():
        if any(kw in low for kw in keywords):
            return category
    return "Main Pages"


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def generate_llmstxt(url: str, max_pages: int = 30, fetcher: Fetcher | None = None) -> dict:
    """Generate llms.txt and llms-full.txt by crawling the site."""
    fetcher = fetcher or DefaultFetcher()
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    try:
        resp = fetcher.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "lxml")
    except Exception as e:
        return {"error": f"Failed to fetch homepage: {e}"}

    title_tag = soup.find("title")
    site_name = title_tag.get_text(strip=True).split("|")[0].split("-")[0].strip() if title_tag else parsed.netloc
    meta_desc = soup.find("meta", attrs={"name": "description"})
    site_desc = meta_desc.get("content", "") if meta_desc else f"Official website of {site_name}"

    pages: dict[str, list[dict]] = {
        "Main Pages": [],
        "Products & Services": [],
        "Resources & Blog": [],
        "Company": [],
        "Support": [],
    }

    seen: set[str] = set()
    skip_exts = {".pdf", ".jpg", ".png", ".gif", ".css", ".js"}

    for a in soup.find_all("a", href=True):
        href = urljoin(base, a["href"])
        text = a.get_text(strip=True)
        if not text or len(text) < 2:
            continue
        p = urlparse(href)
        if p.netloc != parsed.netloc or href in seen:
            continue
        if any(href.endswith(ext) for ext in skip_exts):
            continue
        seen.add(href)
        cat = _categorize_path(p.path)
        pages[cat].append({"url": href, "title": text})
        if len(seen) >= max_pages:
            break

    def _build(full: bool = False) -> str:
        lines = [f"# {site_name}", f"> {site_desc}", ""]
        for section, entries in pages.items():
            if not entries:
                continue
            lines.append(f"## {section}")
            for page in (entries if full else entries[:10]):
                lines.append(f"- [{page['title']}]({page['url']})")
            lines.append("")
        lines += [
            "## Contact",
            f"- Website: {base}",
            f"- Email: contact@{parsed.netloc}",
            "",
        ]
        return "\n".join(lines)

    return {
        "generated_llmstxt": _build(full=False),
        "generated_llmstxt_full": _build(full=True),
        "pages_analyzed": len(seen),
        "sections": {k: len(v) for k, v in pages.items()},
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python llmstxt_generator.py <url> [mode]")
        print("Modes: validate (default), generate")
        sys.exit(1)

    target = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "validate"

    if mode == "validate":
        data = validate_llmstxt(target)
    elif mode == "generate":
        data = generate_llmstxt(target)
    else:
        print(f"Unknown mode: {mode}. Use 'validate' or 'generate'.")
        sys.exit(1)

    print(json.dumps(data, indent=2, default=str))
