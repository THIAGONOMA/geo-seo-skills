#!/usr/bin/env python3
"""
Fetch and parse web pages for GEO analysis.
Extracts HTML, text content, meta tags, headers, structured data,
robots.txt directives, and llms.txt presence.
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
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

AI_CRAWLERS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
    "anthropic-ai", "PerplexityBot", "CCBot", "Bytespider",
    "cohere-ai", "Google-Extended", "GoogleOther",
    "Applebot-Extended", "FacebookBot", "Amazonbot",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security", "Content-Security-Policy",
    "X-Frame-Options", "X-Content-Type-Options",
    "Referrer-Policy", "Permissions-Policy",
]


# ---------------------------------------------------------------------------
# Fetcher abstraction (D — Dependency Inversion)
# ---------------------------------------------------------------------------

class PageFetcher(Protocol):
    def get(self, url: str, timeout: int) -> requests.Response: ...


class DefaultFetcher:
    def get(self, url: str, timeout: int = 30) -> requests.Response:
        return requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)


# ---------------------------------------------------------------------------
# Analyzers (S — Single Responsibility)
# ---------------------------------------------------------------------------

class MetaAnalyzer:
    """Extracts meta-level page data (title, description, canonical, headings)."""

    @staticmethod
    def analyze(soup: BeautifulSoup) -> dict:
        title_tag = soup.find("title")
        meta_tags: dict[str, str] = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name", meta.get("property", ""))
            content = meta.get("content", "")
            if name and content:
                meta_tags[name.lower()] = content

        canonical = soup.find("link", rel="canonical")

        headings: list[dict] = []
        h1s: list[str] = []
        for level in range(1, 7):
            for h in soup.find_all(f"h{level}"):
                txt = h.get_text(strip=True)
                headings.append({"level": level, "text": txt})
                if level == 1:
                    h1s.append(txt)

        return {
            "title": title_tag.get_text(strip=True) if title_tag else None,
            "description": meta_tags.get("description"),
            "canonical": canonical.get("href") if canonical else None,
            "meta_tags": meta_tags,
            "h1_tags": h1s,
            "heading_structure": headings,
        }


class StructuredDataExtractor:
    """Extracts JSON-LD structured data from the page."""

    @staticmethod
    def extract(soup: BeautifulSoup) -> tuple[list[dict], list[str]]:
        data: list[dict] = []
        errors: list[str] = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data.append(json.loads(script.string))
            except (json.JSONDecodeError, TypeError):
                errors.append("Invalid JSON-LD detected")
        return data, errors


class SSRDetector:
    """Detects whether the page is server-side rendered."""

    @staticmethod
    def check(soup: BeautifulSoup, word_count: int) -> tuple[bool, list[str]]:
        roots = soup.find_all(id=re.compile(r"(app|root|__next|__nuxt)", re.I))
        errors: list[str] = []
        has_ssr = True
        for root in roots:
            inner = root.get_text(strip=True)
            if len(inner) < 50 and word_count < 200:
                has_ssr = False
                errors.append(
                    f"Possible client-side only rendering: "
                    f"#{root.get('id', 'unknown')} ({word_count} words)"
                )
        return has_ssr, errors


class LinkAnalyzer:
    """Categorizes internal and external links."""

    @staticmethod
    def analyze(soup: BeautifulSoup, base_url: str) -> dict:
        parsed = urlparse(base_url)
        internal: list[dict] = []
        external: list[dict] = []
        for a in soup.find_all("a", href=True):
            href = urljoin(base_url, a["href"])
            txt = a.get_text(strip=True)
            p = urlparse(href)
            if p.netloc == parsed.netloc:
                internal.append({"url": href, "text": txt})
            elif p.scheme in ("http", "https"):
                external.append({"url": href, "text": txt})
        return {"internal_links": internal, "external_links": external}


# ---------------------------------------------------------------------------
# Robots.txt & llms.txt (O — Open/Closed via composition)
# ---------------------------------------------------------------------------

class RobotsTxtAnalyzer:
    """Parses robots.txt with focus on AI crawler directives."""

    def __init__(self, fetcher: PageFetcher | None = None):
        self._fetcher = fetcher or DefaultFetcher()

    def analyze(self, url: str) -> dict:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        result: dict = {
            "url": robots_url,
            "exists": False,
            "ai_crawler_status": {},
            "sitemaps": [],
            "errors": [],
        }

        try:
            resp = self._fetcher.get(robots_url, timeout=15)
        except Exception as e:
            result["errors"].append(f"Error fetching robots.txt: {e}")
            return result

        if resp.status_code != 200:
            result["errors"].append(f"robots.txt returned {resp.status_code}")
            for c in AI_CRAWLERS:
                result["ai_crawler_status"][c] = "NO_ROBOTS_TXT"
            return result

        result["exists"] = True
        result["content"] = resp.text

        agent_rules: dict[str, list[dict]] = {}
        current_agent: str | None = None

        for line in resp.text.split("\n"):
            line = line.strip()
            low = line.lower()
            if low.startswith("user-agent:"):
                current_agent = line.split(":", 1)[1].strip()
                agent_rules.setdefault(current_agent, [])
            elif low.startswith("disallow:") and current_agent:
                path = line.split(":", 1)[1].strip()
                agent_rules[current_agent].append({"directive": "Disallow", "path": path})
            elif low.startswith("allow:") and current_agent:
                path = line.split(":", 1)[1].strip()
                agent_rules[current_agent].append({"directive": "Allow", "path": path})
            elif low.startswith("sitemap:"):
                sm = line.split(":", 1)[1].strip()
                if not sm.startswith("http"):
                    sm = "http" + sm
                result["sitemaps"].append(sm)

        for crawler in AI_CRAWLERS:
            if crawler in agent_rules:
                rules = agent_rules[crawler]
                if any(r["directive"] == "Disallow" and r["path"] == "/" for r in rules):
                    result["ai_crawler_status"][crawler] = "BLOCKED"
                elif any(r["directive"] == "Disallow" and r["path"] for r in rules):
                    result["ai_crawler_status"][crawler] = "PARTIALLY_BLOCKED"
                else:
                    result["ai_crawler_status"][crawler] = "ALLOWED"
            elif "*" in agent_rules:
                wc = agent_rules["*"]
                if any(r["directive"] == "Disallow" and r["path"] == "/" for r in wc):
                    result["ai_crawler_status"][crawler] = "BLOCKED_BY_WILDCARD"
                else:
                    result["ai_crawler_status"][crawler] = "ALLOWED_BY_DEFAULT"
            else:
                result["ai_crawler_status"][crawler] = "NOT_MENTIONED"

        return result


class LlmsTxtChecker:
    """Checks for the presence of llms.txt and llms-full.txt."""

    def __init__(self, fetcher: PageFetcher | None = None):
        self._fetcher = fetcher or DefaultFetcher()

    def check(self, url: str) -> dict:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        result: dict = {
            "llms_txt": {"url": f"{base}/llms.txt", "exists": False, "content": ""},
            "llms_full_txt": {"url": f"{base}/llms-full.txt", "exists": False, "content": ""},
            "errors": [],
        }
        for key, check_url in [
            ("llms_txt", f"{base}/llms.txt"),
            ("llms_full_txt", f"{base}/llms-full.txt"),
        ]:
            try:
                resp = self._fetcher.get(check_url, timeout=15)
                if resp.status_code == 200:
                    result[key]["exists"] = True
                    result[key]["content"] = resp.text
            except Exception as e:
                result["errors"].append(f"Error checking {check_url}: {e}")
        return result


# ---------------------------------------------------------------------------
# Page Fetch orchestrator
# ---------------------------------------------------------------------------

def fetch_page(url: str, timeout: int = 30) -> dict:
    """Fetch a page and return structured analysis data."""
    fetcher = DefaultFetcher()
    try:
        response = fetcher.get(url, timeout)
    except Exception as e:
        return {"url": url, "errors": [str(e)]}

    result: dict = {
        "url": url,
        "status_code": response.status_code,
        "redirect_chain": [
            {"url": r.url, "status": r.status_code} for r in response.history
        ],
        "security_headers": {
            h: response.headers.get(h) for h in SECURITY_HEADERS
        },
    }

    soup = BeautifulSoup(response.text, "lxml")

    result.update(MetaAnalyzer.analyze(soup))

    structured, sd_errors = StructuredDataExtractor.extract(soup)
    result["structured_data"] = structured

    ssr_check_data = SSRDetector.check(soup, 0)

    for el in soup.find_all(["script", "style", "nav", "footer", "header"]):
        el.decompose()

    text = soup.get_text(separator=" ", strip=True)
    result["word_count"] = len(text.split())
    result["text_content"] = text

    result.update(LinkAnalyzer.analyze(soup, url))

    images = []
    for img in soup.find_all("img"):
        images.append({
            "src": img.get("src", ""),
            "alt": img.get("alt", ""),
            "width": img.get("width"),
            "height": img.get("height"),
            "loading": img.get("loading"),
        })
    result["images"] = images

    has_ssr, ssr_errors = SSRDetector.check(
        BeautifulSoup(response.text, "lxml"), result["word_count"]
    )
    result["has_ssr_content"] = has_ssr
    result["errors"] = sd_errors + ssr_errors

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

MODES = {
    "page": lambda url: fetch_page(url),
    "robots": lambda url: RobotsTxtAnalyzer().analyze(url),
    "llms": lambda url: LlmsTxtChecker().check(url),
    "full": lambda url: {
        "page": fetch_page(url),
        "robots": RobotsTxtAnalyzer().analyze(url),
        "llms": LlmsTxtChecker().check(url),
    },
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_page.py <url> [mode]")
        print("Modes: page (default), robots, llms, full")
        sys.exit(1)

    target = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "page"

    handler = MODES.get(mode)
    if not handler:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

    print(json.dumps(handler(target), indent=2, default=str))
