#!/usr/bin/env python3
"""
Citability Scorer — Analyzes content blocks for AI citation readiness.
Scores passages based on how likely AI models are to cite them.

Optimal AI-cited passages are 134-167 words, self-contained,
fact-rich, and structured with clear answer patterns.
"""

import sys
import json
import re
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Required packages not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Scoring Components
# ---------------------------------------------------------------------------

class AnswerBlockScorer:
    """Evaluates how well a passage answers a potential question (30%)."""

    DEFINITION_PATTERNS = [
        r"\b\w+\s+is\s+(?:a|an|the)\s",
        r"\b\w+\s+refers?\s+to\s",
        r"\b\w+\s+means?\s",
        r"\b\w+\s+(?:can be |are )?defined\s+as\s",
        r"\bin\s+(?:simple|other)\s+(?:terms|words)\s*,",
    ]
    AUTHORITY_PATTERN = re.compile(
        r"(?:according to|research shows|studies? (?:show|indicate|suggest|found)"
        r"|data (?:shows|indicates|suggests))",
        re.IGNORECASE,
    )

    @staticmethod
    def score(text: str, words: list[str], heading: Optional[str]) -> int:
        pts = 0

        for pat in AnswerBlockScorer.DEFINITION_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                pts += 15
                break

        first_60 = " ".join(words[:60])
        if any(
            re.search(p, first_60, re.IGNORECASE)
            for p in [
                r"\b(?:is|are|was|were|means?|refers?)\b",
                r"\d+%",
                r"\$[\d,]+",
                r"\d+\s+(?:million|billion|thousand)",
            ]
        ):
            pts += 15

        if heading and heading.endswith("?"):
            pts += 10

        sentences = re.split(r"[.!?]+", text)
        if sentences:
            short_clear = sum(1 for s in sentences if 5 <= len(s.split()) <= 25)
            pts += int((short_clear / len(sentences)) * 10)

        if AnswerBlockScorer.AUTHORITY_PATTERN.search(text):
            pts += 10

        return min(pts, 30)


class SelfContainmentScorer:
    """Measures passage independence from surrounding context (25%)."""

    @staticmethod
    def score(text: str, words: list[str]) -> int:
        wc = len(words)
        pts = 0

        if 134 <= wc <= 167:
            pts += 10
        elif 100 <= wc <= 200:
            pts += 7
        elif 80 <= wc <= 250:
            pts += 4
        elif 30 <= wc <= 400:
            pts += 2

        pronouns = len(
            re.findall(
                r"\b(?:it|they|them|their|this|that|these|those|he|she|his|her)\b",
                text,
                re.IGNORECASE,
            )
        )
        if wc > 0:
            ratio = pronouns / wc
            if ratio < 0.02:
                pts += 8
            elif ratio < 0.04:
                pts += 5
            elif ratio < 0.06:
                pts += 3

        proper = len(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text))
        if proper >= 3:
            pts += 7
        elif proper >= 1:
            pts += 4

        return min(pts, 25)


class ReadabilityScorer:
    """Evaluates structural readability (20%)."""

    @staticmethod
    def score(text: str, words: list[str]) -> int:
        wc = len(words)
        pts = 0
        sentences = re.split(r"[.!?]+", text)

        if sentences:
            avg_len = wc / len(sentences)
            if 10 <= avg_len <= 20:
                pts += 8
            elif 8 <= avg_len <= 25:
                pts += 5
            else:
                pts += 2

        if re.search(
            r"(?:first|second|third|finally|additionally|moreover|furthermore)",
            text,
            re.IGNORECASE,
        ):
            pts += 4

        if re.search(
            r"(?:\d+[\.\)]\s|\b(?:step|tip|point)\s+\d+)",
            text,
            re.IGNORECASE,
        ):
            pts += 4

        if "\n" in text:
            pts += 4

        return min(pts, 20)


class StatisticalDensityScorer:
    """Measures presence of concrete data points (15%)."""

    @staticmethod
    def score(text: str) -> int:
        pts = 0
        pts += min(len(re.findall(r"\d+(?:\.\d+)?%", text)) * 3, 6)
        pts += min(
            len(
                re.findall(
                    r"\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B|K))?",
                    text,
                )
            )
            * 3,
            5,
        )
        pts += min(
            len(
                re.findall(
                    r"\b\d+(?:,\d{3})*(?:\.\d+)?\s+"
                    r"(?:users|customers|pages|sites|companies|businesses|"
                    r"people|percent|times|x\b)",
                    text,
                    re.IGNORECASE,
                )
            )
            * 2,
            4,
        )

        if re.search(r"\b20(?:2[3-6]|1\d)\b", text):
            pts += 2

        source_pats = [
            r"(?:according to|per|from|by)\s+[A-Z]",
            r"(?:Gartner|Forrester|McKinsey|Harvard|Stanford|MIT|Google|"
            r"Microsoft|OpenAI|Anthropic)",
            r"\([A-Z][a-z]+(?:\s+\d{4})?\)",
        ]
        for pat in source_pats:
            if re.search(pat, text):
                pts += 2

        return min(pts, 15)


class UniquenessScorer:
    """Detects original/first-hand signals (10%)."""

    @staticmethod
    def score(text: str) -> int:
        pts = 0

        if re.search(
            r"(?:our (?:research|study|data|analysis|survey|findings)"
            r"|we (?:found|discovered|analyzed|surveyed|measured))",
            text,
            re.IGNORECASE,
        ):
            pts += 5

        if re.search(
            r"(?:case study|for example|for instance|in practice|real-world|hands-on)",
            text,
            re.IGNORECASE,
        ):
            pts += 3

        if re.search(r"(?:using|with|via|through)\s+[A-Z][a-z]+", text):
            pts += 2

        return min(pts, 10)


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------

GRADE_THRESHOLDS = [
    (80, "A", "Highly Citable"),
    (65, "B", "Good Citability"),
    (50, "C", "Moderate Citability"),
    (35, "D", "Low Citability"),
    (0, "F", "Poor Citability"),
]


def _grade(total: int) -> tuple[str, str]:
    for threshold, grade, label in GRADE_THRESHOLDS:
        if total >= threshold:
            return grade, label
    return "F", "Poor Citability"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_passage(text: str, heading: Optional[str] = None) -> dict:
    """Score a single passage for AI citability (0-100)."""
    words = text.split()
    breakdown = {
        "answer_block_quality": AnswerBlockScorer.score(text, words, heading),
        "self_containment": SelfContainmentScorer.score(text, words),
        "structural_readability": ReadabilityScorer.score(text, words),
        "statistical_density": StatisticalDensityScorer.score(text),
        "uniqueness_signals": UniquenessScorer.score(text),
    }
    total = sum(breakdown.values())
    grade, label = _grade(total)

    return {
        "heading": heading,
        "word_count": len(words),
        "total_score": total,
        "grade": grade,
        "label": label,
        "breakdown": breakdown,
        "preview": " ".join(words[:30]) + ("..." if len(words) > 30 else ""),
    }


def analyze_page_citability(url: str) -> dict:
    """Analyze all content blocks on a page for citability."""
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=30,
        )
        resp.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch page: {e}"}

    soup = BeautifulSoup(resp.text, "lxml")
    for el in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "form"]):
        el.decompose()

    blocks: list[dict] = []
    cur_heading = "Introduction"
    cur_paragraphs: list[str] = []

    for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "table"]):
        if el.name.startswith("h"):
            if cur_paragraphs:
                combined = " ".join(cur_paragraphs)
                if len(combined.split()) >= 20:
                    blocks.append({"heading": cur_heading, "content": combined})
            cur_heading = el.get_text(strip=True)
            cur_paragraphs = []
        else:
            txt = el.get_text(strip=True)
            if txt and len(txt.split()) >= 5:
                cur_paragraphs.append(txt)

    if cur_paragraphs:
        combined = " ".join(cur_paragraphs)
        if len(combined.split()) >= 20:
            blocks.append({"heading": cur_heading, "content": combined})

    scored = [score_passage(b["content"], b["heading"]) for b in blocks]

    if scored:
        avg = sum(b["total_score"] for b in scored) / len(scored)
        top5 = sorted(scored, key=lambda x: x["total_score"], reverse=True)[:5]
        bottom5 = sorted(scored, key=lambda x: x["total_score"])[:5]
        optimal = sum(1 for b in scored if 134 <= b["word_count"] <= 167)
    else:
        avg, top5, bottom5, optimal = 0, [], [], 0

    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for b in scored:
        grade_dist[b["grade"]] += 1

    return {
        "url": url,
        "total_blocks_analyzed": len(scored),
        "average_citability_score": round(avg, 1),
        "optimal_length_passages": optimal,
        "grade_distribution": grade_dist,
        "top_5_citable": top5,
        "bottom_5_citable": bottom5,
        "all_blocks": scored,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python citability_scorer.py <url>")
        print("Returns JSON with citability analysis for all content blocks.")
        sys.exit(1)

    result = analyze_page_citability(sys.argv[1])
    print(json.dumps(result, indent=2, default=str))
