# GEO-SEO Analyzer

> GEO-first SEO analysis tool that optimizes websites for AI-powered search engines (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews) while maintaining traditional SEO foundations.

> **Important**: Name and description are in English for marketplace searchability. Workflow and best practices remain in the original language.

## Metadata

- **id**: geo-seo
- **domain**: development
- **subDomain**: frontend
- **complexity**: high
- **version**: 1.0.0
- **agentCompatible**: [cursor, claude-code, codex, copilot]
- **tags**: [geo, seo, ai-search, citability, crawlers, llms-txt, brand-mentions, schema-markup, e-e-a-t, content-quality]

## Triggers

Keywords that activate this skill when detected by the agent:

- "geo audit"
- "seo audit"
- "AI search optimization"
- "citability score"
- "AI crawler analysis"
- "llms.txt"
- "brand mentions"
- "schema markup"
- "GEO report"
- "optimize for AI search"
- "AI visibility"
- "e-e-a-t assessment"
- "structured data analysis"
- "platform-specific optimization"

## Cognitive Phases

The cognitive phases define the **reasoning order** the agent follows when executing this skill.

### 1. SENSE — Perception

> The agent captures signals from the environment: reads pages, fetches data, observes state.

- Fetch homepage HTML via WebFetch or curl
- Extract sitemap.xml and internal links (up to 50 pages)
- Read robots.txt for AI crawler configuration
- Detect business type (SaaS, Local Service, E-commerce, Publisher, Agency)
- Identify existing structured data (JSON-LD, microdata)

### 2. CONTEXTUALIZE — Contextualization

> The agent understands context: loads configs, project patterns, history.

- Identify the business type and adjust recommendations accordingly
- Map content structure: blog posts, product pages, landing pages
- Check for existing llms.txt file
- Scan for brand mentions across AI-cited platforms (YouTube, Reddit, Wikipedia, LinkedIn)
- Identify current schema markup and its completeness

### 3. HYPOTHESIZE — Hypothesis

> The agent generates hypotheses and plans: possibilities, approaches.

- Generate citability scores for content blocks (optimal: 134-167 words per passage)
- Identify AI crawler access issues in robots.txt
- Detect missing or incomplete structured data
- Map platform-specific optimization gaps (ChatGPT, Perplexity, Google AIO)
- Assess E-E-A-T signals (expertise, experience, authority, trust)

### 4. EVALUATE — Evaluation

> The agent evaluates alternatives: classifies, prioritizes, validates.

- Score each dimension with weighted methodology:
  - AI Citability & Visibility: 25%
  - Brand Authority Signals: 20%
  - Content Quality & E-E-A-T: 20%
  - Technical Foundations: 15%
  - Structured Data: 10%
  - Platform Optimization: 10%
- Calculate composite GEO Score (0-100)
- Classify findings by severity: Critical, High, Medium, Low

### 5. RECOMMEND — Recommendation

> The agent recommends actions: suggestions, reviews, reports.

- Generate prioritized action plan:
  - Quick Wins (immediate impact, low effort)
  - Medium-Term improvements
  - Strategic long-term changes
- Produce client-ready GEO report in Markdown
- Generate JSON-LD schemas where missing
- Create or improve llms.txt file
- Provide platform-specific recommendations

### 6. ACT — Action

> The agent executes: generates files, writes reports, deploys fixes.

- Generate `GEO-AUDIT-REPORT.md` with full analysis
- Generate or validate `llms.txt` file
- Generate missing JSON-LD structured data
- Create platform-specific optimization checklist
- Output `GEO-REPORT.pdf` with charts and visualizations (if requested)

### 7. REFLECT — Reflection

> The agent reflects on the outcome: validates, learns, documents.

- Validate that generated schemas are valid JSON-LD
- Confirm llms.txt follows the emerging standard
- Compare GEO Score against industry benchmarks
- Report telemetry via SkillsChain MCP
- Suggest follow-up audits and monitoring schedule

## Workflow

Step-by-step skill execution referencing cognitive phases:

0. **SETUP** — Download Resources
   - Clone or download scripts from `https://github.com/THIAGONOMA/geo-seo-skills`
   - Place them in `skillschain/resources/geo-seo/`
   - Install Python dependencies: `pip install -r skillschain/resources/geo-seo/requirements.txt`
   - Verify scripts are available: `ls skillschain/resources/geo-seo/scripts/`

1. **SENSE** — Discovery Phase
   - Fetch homepage HTML via {{MCP: mcp-browser}} or WebFetch
   - Extract key pages from sitemap.xml or internal links (max 50 pages)
   - Read and parse robots.txt for AI crawler directives
   - Detect business type by analyzing homepage patterns

2. **CONTEXTUALIZE** — Parallel Analysis
   - Run resource scripts for data collection:
     - `python skillschain/resources/geo-seo/scripts/fetch_page.py <url> full`
     - `python skillschain/resources/geo-seo/scripts/citability_scorer.py <url>`
     - `python skillschain/resources/geo-seo/scripts/brand_scanner.py "<brand>" <domain>`
     - `python skillschain/resources/geo-seo/scripts/llmstxt_generator.py <url> validate`
   - Analyze outputs across 5 tracks: AI Visibility, Platform, Technical, Content, Schema

3. **HYPOTHESIZE** — Score each content block
   - Use `citability_scorer.py` output to evaluate passages (134-167 word optimal blocks)
   - Use `fetch_page.py robots` output to check 14+ AI crawlers
   - Use `brand_scanner.py` output to map brand presence across 10+ platforms

4. **EVALUATE** — Composite scoring
   - Calculate weighted GEO Score (0-100)
   - Classify all findings by severity and impact
   - Prioritize by effort-to-impact ratio

5. **RECOMMEND** — Generate deliverables
   - Produce structured GEO audit report
   - Generate missing JSON-LD schemas
   - Create or improve llms.txt
   - Build prioritized action plan

6. **ACT** — Output files
   - Write `GEO-AUDIT-REPORT.md`
   - Write `llms.txt` if needed
   - Write JSON-LD snippets for implementation
   - Optionally generate PDF report with charts

7. **REFLECT** — Validation and telemetry
   - Validate generated assets
   - Report execution telemetry via {{MCP: mcp-skillschain}}
   - Suggest monitoring cadence

## Best Practices

- Always respect robots.txt — never crawl blocked paths
- Limit to 50 pages per audit for quality over quantity
- Add 1-second delay between requests, max 5 concurrent fetches
- Optimal AI-cited passages are 134-167 words, self-contained and fact-rich
- Brand mentions correlate 3x more strongly with AI visibility than backlinks
- Only 11% of domains are cited by both ChatGPT and Google AIO for the same query — tailor recommendations per platform
- Always validate generated JSON-LD before recommending deployment
- Adjust recommendations based on detected business type (SaaS vs Local vs E-commerce)
- Consider the site's current maturity level — don't overwhelm with 100 changes

## MCP Servers

Tools (Model Context Protocol) required by this skill.

### mcp-browser

- **type**: browser
- **required**: true
- **auth**:
  - **strategy**: agent-resolved
  - **instructions**: Requires Chrome/Chromium installed locally. The agent uses it for page fetching, screenshots and rendering analysis.
- **description**: Web navigation, page fetching, rendering analysis and screenshots for visual audit.

### mcp-skillschain

- **type**: api
- **required**: false
- **auth**:
  - **strategy**: agent-resolved
  - **instructions**: Connects to SkillsChain MCP Server automatically.
- **description**: Report execution telemetry and skill rating via `report_execution` and `rate_skill`.

## Resources

Python scripts included in this skill repository that serve as analysis utilities.
The agent **must** download them before execution.

**Repository:** `https://github.com/THIAGONOMA/geo-seo-skills`
**Local path:** `skillschain/resources/geo-seo/`

| Script | Description |
|--------|-------------|
| `scripts/citability_scorer.py` | AI citability scoring per content block (0-100). Evaluates answer quality, self-containment, readability, statistical density and uniqueness. |
| `scripts/fetch_page.py` | Page fetcher with modes: `page` (HTML + meta + headings), `robots` (AI crawler directives for 14+ bots), `llms` (llms.txt detection), `full` (all combined). |
| `scripts/brand_scanner.py` | Brand mention scanner across YouTube, Reddit, Wikipedia, LinkedIn and 7 other platforms. Includes live Wikipedia/Wikidata API checks. |
| `scripts/llmstxt_generator.py` | Validates existing llms.txt format or generates one by crawling the site and categorizing pages. |

**Dependencies:** `pip install -r requirements.txt` (requests, beautifulsoup4, lxml)

## Post-Execution Callbacks

After executing this skill, the agent **MUST** report telemetry and **MAY** send a rating.
These data feed the ranking and ecosystem quality.

### 1. Telemetry (MANDATORY)

Call `report_execution` via MCP SkillsChain after **every** execution:

```
report_execution({
  skillId: "geo-seo",
  agentPlatform: "cursor",
  success: true,
  latencyMs: 45000,
  tokensUsed: 25000,
  hallucinationDetected: false,
  phasesExecuted: ["SENSE", "CONTEXTUALIZE", "HYPOTHESIZE", "EVALUATE", "RECOMMEND", "ACT", "REFLECT"],
  errorType: null,
  notes: "Full GEO audit on example.com — GEO Score: 72/100, 15 findings"
})
```

**Mandatory fields**: `skillId`, `agentPlatform`, `success`, `latencyMs`
**Impact**: Feeds the β (Agent) component of CompositeScore and the Telemetry panel.

### 2. Rating (RECOMMENDED)

Call `rate_skill` via MCP SkillsChain for qualitative evaluation:

```
rate_skill({
  skillId: "geo-seo",
  agentPlatform: "cursor",
  stars: 4,
  successRate: 0.92,
  latencyMs: 45000,
  tokensUsed: 25000,
  feedback: "Comprehensive audit with actionable insights, PDF generation was excellent"
})
```

**Impact**: Feeds the α (Human) component of CompositeScore and triggers automatic recalculation.

### Complete post-execution flow

1. Execute the skill normally following the Workflow
2. **ALWAYS** call `report_execution` with telemetry data
3. **OPTIONALLY** call `rate_skill` with qualitative evaluation
4. CompositeScore is recalculated automatically

## Dependencies

Skills this skill depends on to function:

- (no mandatory dependencies — autonomous skill)

## Associated Skills

Skills that complement or are frequently used together:

- web-scraper
- security-scanner
- rest-api-builder

---

## Repository Structure

```
geo-seo-skills/
├── SKILL.md                        # This document (SkillsChain standard)
├── README.md                       # Description for humans
├── LICENSE                         # MIT License
├── requirements.txt                # Python dependencies
├── scripts/                        # Resource scripts (downloadable)
│   ├── citability_scorer.py        # AI citability scoring (0-100)
│   ├── fetch_page.py               # Page fetch + robots.txt + llms.txt
│   ├── brand_scanner.py            # Brand mention scanner
│   └── llmstxt_generator.py        # llms.txt validator & generator
├── examples/                       # Usage examples
│   └── full-audit-example.md       # Complete 7-phase GEO audit
└── tests/                          # Test scenarios
    └── test-scenarios.md           # Scenarios for all scripts
```

## Publication Checklist

- [x] SKILL.md fully completed
- [x] Name and description in English
- [x] At least 2 triggers defined (14 triggers)
- [x] At least 2 cognitive phases selected (7 phases)
- [x] Detailed workflow with resource script references
- [x] Best practices documented (9 practices)
- [x] Resources section with downloadable scripts
- [x] README.md for humans
- [x] Public repository on GitHub
