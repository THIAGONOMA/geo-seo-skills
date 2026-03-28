# 🌐 GEO-SEO Analyzer — SkillsChain Skill

**Otimiza websites para mecanismos de busca AI-powered (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews).**

[![SkillsChain Compatible](https://img.shields.io/badge/SkillsChain-v1.0-818cf8)](https://github.com/THIAGONOMA/skillschain)
[![GEO-First](https://img.shields.io/badge/GEO--first-SEO%20supported-34d399)](.)
[![Platforms](https://img.shields.io/badge/Cursor%20%7C%20Claude%20%7C%20Codex%20%7C%20Copilot-compatible-38bdf8)](.)
[![Python Scripts](https://img.shields.io/badge/scripts-Python%203.8+-fbbf24)](.)

> **Filosofia:** GEO-first, SEO-supported. AI search está comendo o search tradicional. Esta ferramenta otimiza para onde o tráfego está indo, não onde ele estava.

---

## Por que GEO importa (2026)

| Métrica | Valor |
|---------|-------|
| Mercado de serviços GEO | $850M+ (projetado $7.3B até 2031) |
| Crescimento de tráfego via AI | +527% ano a ano |
| Conversão AI vs. orgânico | 4.4x maior |
| Gartner: queda de tráfego search até 2028 | -50% |
| Brand mentions vs. backlinks para AI | 3x mais forte correlação |
| Marketers investindo em GEO | Apenas 23% |

## O que faz?

Este skill instrui agentes IA a realizarem **auditorias GEO completas** em websites:

| Componente | Análise |
|------------|---------|
| **Citability** | Score de prontidão para citação por IA (passagens 134-167 palavras) |
| **AI Crawlers** | Análise de robots.txt para 14+ crawlers (GPTBot, ClaudeBot, PerplexityBot) |
| **Brand Mentions** | Presença em YouTube, Reddit, Wikipedia, LinkedIn (3x mais impacto que backlinks) |
| **llms.txt** | Geração e validação do padrão emergente llms.txt |
| **Schema Markup** | Detecção, validação e geração de JSON-LD estruturado |
| **E-E-A-T** | Avaliação de Expertise, Experience, Authority, Trust |
| **Platform-specific** | Otimização para ChatGPT, Perplexity, Google AI Overviews |

## Diferenciais

- **Scripts Python incluídos** — citability scorer, brand scanner, page fetcher, llms.txt generator
- **GEO Score composto** — ponderação: Citability 25%, Brand 20%, E-E-A-T 20%, Technical 15%, Schema 10%, Platform 10%
- **Multi-plataforma** — funciona com Cursor, Claude Code, Codex, Copilot
- **7 fases cognitivas** — pipeline completo de análise

## Como Usar

### 1. Com Cursor (`.mdc`)

Baixe o skill via MCP SkillsChain:

```bash
search_skills({ query: "geo seo audit" })
download_skill({ skillId: "geo-seo", platform: "cursor" })
```

Depois basta pedir ao agente:

> "Faça uma auditoria GEO completa de https://example.com"

> "Analise o citability score de https://example.com/blog"

> "Verifique os AI crawlers do meu site"

> "Gere um llms.txt para https://example.com"

### 2. Com Claude Code

```bash
download_skill({ skillId: "geo-seo", platform: "claude-code" })
```

### 3. Com Codex / Copilot

```bash
download_skill({ skillId: "geo-seo", platform: "codex" })
```

## Fases Cognitivas

O skill utiliza **todas as 7 fases cognitivas** do SkillsChain:

```
SENSE → CONTEXTUALIZE → HYPOTHESIZE → EVALUATE → RECOMMEND → ACT → REFLECT
  📡         🔍              💡           ⚖️          📋       ⚡      🪞
Fetch     Mapeamento      Scoring     Ponderação   Action   Gera      Valida
páginas   do site         citability  composite    plan     reports   assets
```

## Scripts Python

Scripts utilitários incluídos em `scripts/`:

| Script | Uso |
|--------|-----|
| `fetch_page.py` | Fetch e parsing de páginas (HTML, meta tags, structured data, robots.txt) |
| `citability_scorer.py` | Score de citabilidade AI por bloco de conteúdo (0-100) |
| `brand_scanner.py` | Scan de presença de marca em YouTube, Reddit, Wikipedia, LinkedIn |
| `llmstxt_generator.py` | Validação e geração de llms.txt |

```bash
pip install -r requirements.txt

python scripts/fetch_page.py https://example.com
python scripts/citability_scorer.py https://example.com
python scripts/brand_scanner.py "Minha Marca" meusite.com
python scripts/llmstxt_generator.py https://example.com generate
```

## Exemplo de Output

**GEO Score: 68/100**

```
AI Citability & Visibility  ████████░░ 72% (25%)
Brand Authority Signals     █████░░░░░ 55% (20%)
Content Quality & E-E-A-T   ███████░░░ 70% (20%)
Technical Foundations       ████████░░ 82% (15%)
Structured Data             ██████░░░░ 60% (10%)
Platform Optimization       █████░░░░░ 48% (10%)
```

## Estrutura do Repositório

```
geo-seo-skills/
├── SKILL.md              # Documento principal (SkillsChain standard)
├── README.md             # Este arquivo
├── LICENSE               # MIT License
├── requirements.txt      # Dependências Python
├── scripts/              # Utilitários Python
│   ├── fetch_page.py     # Page fetcher & parser
│   ├── citability_scorer.py  # AI citability scoring
│   ├── brand_scanner.py  # Brand mention detection
│   └── llmstxt_generator.py  # llms.txt validator & generator
├── examples/             # Exemplos de uso
│   └── full-audit-example.md
└── tests/                # Cenários de teste
    └── test-scenarios.md
```

## Licença

MIT — use livremente em qualquer projeto.

---

**Adaptado de [zubair-trabzada/geo-seo-claude](https://github.com/zubair-trabzada/geo-seo-claude) para o padrão [SkillsChain](https://github.com/THIAGONOMA/skillschain).**

**Publicado por [@thiagonobredev](https://github.com/thiagonobredev) via [SkillsChain](https://github.com/THIAGONOMA/skillschain)**
