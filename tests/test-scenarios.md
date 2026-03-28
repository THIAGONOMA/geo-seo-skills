# Cenários de Teste — GEO-SEO Analyzer

## 1. Citability Scorer

### 1.1 Passagem Altamente Citável (Grade A)

**Input:**
```
According to Gartner's 2025 report, AI-powered search engines will handle 35% of all search queries by 2028. The study analyzed 1.2 million queries across Google, Bing, ChatGPT, and Perplexity, finding that sites with optimized AI citability scores saw 4.4x higher conversion rates compared to traditional organic traffic. Businesses investing in Generative Engine Optimization reported an average revenue increase of 23% within six months of implementation.
```

**Resultado esperado:**
- `total_score` >= 75
- `grade`: "A" ou "B"
- `answer_block_quality` >= 20 (definições + autoridade)
- `statistical_density` >= 10 (percentagens + números)

### 1.2 Passagem Fraca (Grade D/F)

**Input:**
```
It is really good and they should do it because it helps.
```

**Resultado esperado:**
- `total_score` < 35
- `grade`: "D" ou "F"
- `self_containment` baixo (pronomes + pouco conteúdo)

---

## 2. Fetch Page

### 2.1 Página com SSR

**URL de teste:** `https://nextjs.org`

**Verificações:**
- `has_ssr_content`: `true`
- `title`: não nulo
- `heading_structure`: contém elementos
- `structured_data`: pelo menos 1 JSON-LD

### 2.2 robots.txt com AI crawlers bloqueados

**URL de teste:** `https://nytimes.com`

**Verificações:**
- `ai_crawler_status.GPTBot`: `"BLOCKED"`
- `ai_crawler_status.ClaudeBot`: `"BLOCKED"` ou `"NOT_MENTIONED"`

### 2.3 Modo Full

**Verificações:**
- Retorna `page`, `robots`, `llms` como sub-objetos
- Nenhum campo com erro fatal

---

## 3. Brand Scanner

### 3.1 Marca conhecida

**Input:** `brand_name = "OpenAI"`

**Verificações:**
- `platforms.wikipedia.has_wikipedia_page`: `true`
- `platforms.wikipedia.has_wikidata_entry`: `true`
- `platforms.youtube.search_url`: contém "OpenAI"
- `overall_recommendations`: lista não vazia

### 3.2 Marca desconhecida

**Input:** `brand_name = "XyzRandomBrand12345"`

**Verificações:**
- `platforms.wikipedia.has_wikipedia_page`: `false`
- `platforms.wikipedia.has_wikidata_entry`: `false`
- Nenhum crash

---

## 4. llms.txt Generator

### 4.1 Validação de site com llms.txt

**URL de teste:** `https://docs.anthropic.com`

**Verificações:**
- Se `exists: true`: `format_valid` é boolean, `issues` e `suggestions` são listas

### 4.2 Geração para site sem llms.txt

**URL de teste:** qualquer site sem `/llms.txt`

**Verificações:**
- `generated_llmstxt` começa com `# `
- `generated_llmstxt` contém pelo menos 1 seção `## `
- `generated_llmstxt` contém links no formato `- [title](url)`
- `pages_analyzed` > 0

---

## 5. Integração E2E

### 5.1 Auditoria completa

**Fluxo:**
1. `fetch_page.py <url> full` — sucesso sem erros
2. `citability_scorer.py <url>` — retorna `all_blocks` com pelo menos 1 entry
3. `brand_scanner.py "Brand" domain.com` — retorna 5 plataformas
4. `llmstxt_generator.py <url> validate` — retorna resultado de validação

**Critério:** Todas as 4 etapas completam sem exceções.

---

## Execução dos Testes

```bash
pip install -r requirements.txt

python scripts/citability_scorer.py https://example.com
python scripts/fetch_page.py https://example.com full
python scripts/brand_scanner.py "Example" example.com
python scripts/llmstxt_generator.py https://example.com validate
```

Todos os comandos devem retornar JSON válido sem erros fatais.
