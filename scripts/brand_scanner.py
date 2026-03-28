#!/usr/bin/env python3
"""
Brand Mention Scanner — Checks brand presence across AI-cited platforms.

Brand mentions correlate 3x more strongly with AI visibility than backlinks.
(Ahrefs December 2025 study of 75,000 brands)

Platform importance for AI citations:
1. YouTube mentions  (~0.737 correlation — STRONGEST)
2. Reddit mentions   (high)
3. Wikipedia presence (high)
4. LinkedIn presence  (moderate)
5. Domain Rating      (~0.266 — weak)
"""

import sys
import json
from urllib.parse import quote_plus
from typing import Protocol

try:
    import requests
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
}


# ---------------------------------------------------------------------------
# Platform checker abstraction (O — Open/Closed, I — Interface Segregation)
# ---------------------------------------------------------------------------

class PlatformChecker(Protocol):
    """Each platform checker only handles its own concern."""

    def check(self, brand_name: str) -> dict: ...


class YouTubeChecker:
    CORRELATION = 0.737
    WEIGHT = "25%"

    def check(self, brand_name: str) -> dict:
        return {
            "platform": "YouTube",
            "correlation": self.CORRELATION,
            "weight": self.WEIGHT,
            "search_url": f"https://www.youtube.com/results?search_query={quote_plus(brand_name)}",
            "check_instructions": [
                f"Search YouTube for '{brand_name}' and check:",
                "1. Does the brand have an official YouTube channel?",
                "2. Are there videos FROM the brand (tutorials, demos)?",
                "3. Are there videos ABOUT the brand from other creators?",
                "4. What is the view count on brand-related videos?",
                "5. Are there positive reviews or demonstrations?",
            ],
            "recommendations": [
                "Create a YouTube channel if none exists",
                "Publish educational/tutorial content related to your niche",
                "Encourage customers to create review/demo videos",
                "Optimize video titles and descriptions with brand name",
                "Add timestamps, chapters, and transcripts for AI parseability",
            ],
        }


class RedditChecker:
    WEIGHT = "25%"

    def check(self, brand_name: str) -> dict:
        return {
            "platform": "Reddit",
            "correlation": "High",
            "weight": self.WEIGHT,
            "search_url": f"https://www.reddit.com/search/?q={quote_plus(brand_name)}",
            "check_instructions": [
                f"Search Reddit for '{brand_name}' and check:",
                "1. Does the brand have its own subreddit?",
                "2. Is it discussed in relevant industry subreddits?",
                "3. What is the sentiment (positive/negative/neutral)?",
                "4. Are there recommendation threads mentioning the brand?",
                "5. Are mentions recent (within last 6 months)?",
            ],
            "recommendations": [
                "Monitor relevant subreddits for brand mentions",
                "Participate authentically — no marketing speak",
                "Create an official Reddit account for support",
                "Share valuable content (not self-promotion)",
            ],
        }


class WikipediaChecker:
    WEIGHT = "20%"

    def check(self, brand_name: str) -> dict:
        result: dict = {
            "platform": "Wikipedia",
            "correlation": "High",
            "weight": self.WEIGHT,
            "has_wikipedia_page": False,
            "has_wikidata_entry": False,
            "search_url": (
                f"https://en.wikipedia.org/wiki/Special:Search"
                f"?search={quote_plus(brand_name)}"
            ),
            "recommendations": [
                "If eligible, create a Wikipedia article (requires notability)",
                "Ensure Wikidata entry exists with structured data",
                "Add sameAs links in schema markup to Wikipedia/Wikidata",
                "Build notability through press coverage and independent reviews",
            ],
        }

        try:
            api = (
                f"https://en.wikipedia.org/w/api.php?action=query&list=search"
                f"&srsearch={quote_plus(brand_name)}&format=json"
            )
            resp = requests.get(api, headers=DEFAULT_HEADERS, timeout=15)
            if resp.ok:
                hits = resp.json().get("query", {}).get("search", [])
                if hits and brand_name.lower() in hits[0].get("title", "").lower():
                    result["has_wikipedia_page"] = True
                result["wikipedia_search_results"] = len(hits)
        except Exception:
            pass

        try:
            wd = (
                f"https://www.wikidata.org/w/api.php?action=wbsearchentities"
                f"&search={quote_plus(brand_name)}&language=en&format=json"
            )
            resp = requests.get(wd, headers=DEFAULT_HEADERS, timeout=15)
            if resp.ok:
                entities = resp.json().get("search", [])
                if entities:
                    result["has_wikidata_entry"] = True
                    result["wikidata_id"] = entities[0].get("id", "")
                    result["wikidata_description"] = entities[0].get("description", "")
        except Exception:
            pass

        return result


class LinkedInChecker:
    WEIGHT = "15%"

    def check(self, brand_name: str) -> dict:
        return {
            "platform": "LinkedIn",
            "correlation": "Moderate",
            "weight": self.WEIGHT,
            "search_url": (
                f"https://www.linkedin.com/search/results/companies/"
                f"?keywords={quote_plus(brand_name)}"
            ),
            "check_instructions": [
                f"Search LinkedIn for '{brand_name}' and check:",
                "1. Does the company have a LinkedIn page?",
                "2. How many followers?",
                "3. Is the page active with recent posts?",
                "4. Do employees post thought leadership content?",
            ],
            "recommendations": [
                "Create/optimize LinkedIn company page",
                "Post regular thought leadership content",
                "Encourage employees to share company content",
                "Publish long-form LinkedIn articles",
            ],
        }


class OtherPlatformsChecker:
    WEIGHT = "15%"
    PLATFORMS = {
        "Quora": "https://www.quora.com/search?q={}",
        "Stack Overflow": "https://stackoverflow.com/search?q={}",
        "GitHub": "https://github.com/search?q={}",
        "Crunchbase": "https://www.crunchbase.com/textsearch?q={}",
        "Product Hunt": "https://www.producthunt.com/search?q={}",
        "G2": "https://www.g2.com/search?utf8=&query={}",
        "Trustpilot": "https://www.trustpilot.com/search?query={}",
    }

    def check(self, brand_name: str) -> dict:
        encoded = quote_plus(brand_name)
        return {
            "platform": "Other Platforms",
            "weight": self.WEIGHT,
            "platforms_checked": {
                name: {"search_url": url.format(encoded)}
                for name, url in self.PLATFORMS.items()
            },
            "recommendations": [
                "Maintain profiles on industry-relevant platforms",
                "Respond to questions on Quora and Stack Overflow",
                "Encourage reviews on G2 and Trustpilot",
                "Keep Crunchbase profile updated (important for B2B)",
                "Open-source on GitHub boosts developer brand authority",
            ],
        }


# ---------------------------------------------------------------------------
# Report generator (D — depends on abstractions)
# ---------------------------------------------------------------------------

DEFAULT_CHECKERS: list[tuple[str, PlatformChecker]] = [
    ("youtube", YouTubeChecker()),
    ("reddit", RedditChecker()),
    ("wikipedia", WikipediaChecker()),
    ("linkedin", LinkedInChecker()),
    ("other", OtherPlatformsChecker()),
]


def generate_brand_report(
    brand_name: str,
    domain: str | None = None,
    checkers: list[tuple[str, PlatformChecker]] | None = None,
) -> dict:
    """Generate a comprehensive brand mention report."""
    checkers = checkers or DEFAULT_CHECKERS

    report: dict = {
        "brand_name": brand_name,
        "domain": domain,
        "key_insight": (
            "Brand mentions correlate 3x more strongly with AI visibility "
            "than backlinks (Ahrefs Dec 2025, 75K brands)"
        ),
        "platforms": {},
        "overall_recommendations": [
            "Priority 1: YouTube — highest correlation (0.737). Create educational content.",
            "Priority 2: Reddit — authentic presence in industry subreddits.",
            "Priority 3: Wikipedia — establish notability, then create/improve entry.",
            "Priority 4: LinkedIn — thought leadership from founders and employees.",
            "Priority 5: Review platforms — G2, Trustpilot for social proof signals.",
            "Cross-platform: consistent NAP (Name, Address, Phone) everywhere.",
            "Schema: add sameAs linking to ALL platform profiles.",
        ],
    }

    for key, checker in checkers:
        report["platforms"][key] = checker.check(brand_name)

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python brand_scanner.py <brand_name> [domain]")
        print("Example: python brand_scanner.py 'Acme Corp' acmecorp.com")
        sys.exit(1)

    brand = sys.argv[1]
    dom = sys.argv[2] if len(sys.argv) > 2 else None
    print(json.dumps(generate_brand_report(brand, dom), indent=2, default=str))
