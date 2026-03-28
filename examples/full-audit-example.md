# Exemplo de Auditoria GEO Completa

## Cenário

Usuário pede ao agente:

> "Faça uma auditoria GEO completa de https://example.com"

---

## Fase 1 — SENSE (Coleta)

O agente executa os scripts de coleta:

```bash
python scripts/fetch_page.py https://example.com full
python scripts/citability_scorer.py https://example.com
python scripts/brand_scanner.py "Example Corp" example.com
python scripts/llmstxt_generator.py https://example.com validate
```

### Output esperado (fetch_page — mode: robots)

```json
{
  "url": "https://example.com/robots.txt",
  "exists": true,
  "ai_crawler_status": {
    "GPTBot": "NOT_MENTIONED",
    "ClaudeBot": "NOT_MENTIONED",
    "PerplexityBot": "NOT_MENTIONED",
    "Google-Extended": "BLOCKED"
  }
}
```

**Diagnóstico:** Google-Extended está bloqueado, mas os principais crawlers AI não estão mencionados — oportunidade de otimização.

---

## Fase 2 — CONTEXTUALIZE (Mapeamento)

O agente mapeia a estrutura do site:

| Aspecto | Status |
|---------|--------|
| SSR/Prerendering | Sim (Next.js) |
| JSON-LD Schema | Presente (Organization) |
| Headings H1 | 1 por página |
| Meta description | Presente |
| llms.txt | Não existe |
| Sitemap | Presente (45 URLs) |

---

## Fase 3 — HYPOTHESIZE (Scoring)

### GEO Score Breakdown

```
AI Citability & Visibility  ████████░░ 72% (peso 25%)
Brand Authority Signals     █████░░░░░ 55% (peso 20%)
Content Quality & E-E-A-T   ███████░░░ 70% (peso 20%)
Technical Foundations       ████████░░ 82% (peso 15%)
Structured Data             ██████░░░░ 60% (peso 10%)
Platform Optimization       █████░░░░░ 48% (peso 10%)
─────────────────────────────────────────────────────
GEO SCORE TOTAL             ██████░░░░ 65/100
```

---

## Fase 4 — EVALUATE (Priorização)

| Prioridade | Ação | Impacto | Esforço |
|------------|------|---------|---------|
| 1 | Criar llms.txt | Alto | Baixo |
| 2 | Adicionar sameAs no schema | Alto | Baixo |
| 3 | Otimizar passagens para citabilidade (134-167 palavras) | Alto | Médio |
| 4 | Aumentar presença YouTube | Alto | Alto |
| 5 | Desbloquear Google-Extended | Médio | Baixo |
| 6 | Adicionar FAQ schema | Médio | Baixo |
| 7 | Expandir JSON-LD (Article, FAQPage) | Médio | Médio |

---

## Fase 5 — RECOMMEND (Plano)

O agente apresenta o plano de ação com estimativas de impacto no GEO Score:

> **Impacto projetado:** 65 → 82 (+17 pontos) implementando as 7 ações acima.

---

## Fase 6 — ACT (Execução)

O agente gera os assets:

1. **llms.txt** via `python scripts/llmstxt_generator.py https://example.com generate`
2. **Schema JSON-LD** expandido com `sameAs`, `FAQPage`, `Article`
3. **Passagens otimizadas** — reescrita de 5 blocos top para 134-167 palavras
4. **robots.txt atualizado** — `Allow: /` para GPTBot, ClaudeBot, PerplexityBot

---

## Fase 7 — REFLECT (Validação)

```json
{
  "geo_score_before": 65,
  "geo_score_after": 79,
  "improvement": "+14 pontos",
  "actions_completed": 5,
  "actions_pending": 2,
  "note": "YouTube e conteúdo E-E-A-T requerem ações de longo prazo"
}
```

---

## Telemetria SkillsChain

```json
report_execution({
  "skillId": "geo-seo",
  "success": true,
  "latencyMs": 12500,
  "tokensUsed": 8200,
  "hallucinationDetected": false,
  "platform": "cursor"
})

rate_skill({
  "skillId": "geo-seo",
  "rating": 5,
  "comment": "Auditoria completa com assets prontos para deploy"
})
```
