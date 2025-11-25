# Contrato da API - Endpoint de Q&A

## Endpoint Principal

**POST** `/api/v1/query`

Endpoint único para realizar perguntas sobre os documentos indexados no sistema RAG.

---

## Request (Requisição)

### Headers

```
Content-Type: application/json
```

### Body (QueryRequest)

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| `question` | `string` | ✅ Sim | Pergunta do usuário sobre os documentos | `"Qual é o horário de funcionamento?"` |
| `top_k` | `integer` | ❌ Não | Número de documentos a recuperar do vector store. Se não informado, usa o valor padrão configurado (geralmente 5) | `3` |

### Exemplo de Request

```json
{
  "question": "Quais são os principais serviços oferecidos?",
  "top_k": 5
}
```

**Request mínimo (sem top_k):**

```json
{
  "question": "Qual é o horário de funcionamento?"
}
```

---

## Response (Resposta)

### Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| `200` | Sucesso - Resposta gerada ou bloqueada pelos guardrails |
| `500` | Erro interno do servidor |

### Body (QueryResponse)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `answer` | `string \| null` | ✅ Sim | Resposta gerada pelo LLM. Será `null` se a requisição foi bloqueada pelos guardrails |
| `citations` | `array[Citation]` | ✅ Sim | Lista de documentos fonte utilizados para gerar a resposta |
| `metrics` | `Metrics` | ✅ Sim | Métricas de execução (latência, tokens, custo) |
| `guardrail_status` | `GuardrailStatus` | ✅ Sim | Status dos guardrails de segurança |
| `timestamp` | `datetime` | ✅ Sim | Timestamp ISO 8601 da requisição |

#### Citation (Objeto de Citação)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `source` | `string` | ✅ Sim | Nome do documento fonte | `"documento.pdf"` |
| `excerpt` | `string` | ✅ Sim | Trecho relevante do documento (máximo ~500 caracteres) | `"O horário de funcionamento é..."` |
| `page` | `integer \| null` | ❌ Não | Número da página do documento (se aplicável) | `5` |
| `relevance_score` | `float` | ✅ Sim | Score de relevância do documento (0.0 a 1.0) | `0.85` |

#### Metrics (Métricas)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `total_latency_ms` | `float` | ✅ Sim | Latência total da requisição em milissegundos | `1250.5` |
| `retrieval_latency_ms` | `float` | ✅ Sim | Latência do processo de retrieval (busca no vector store) em milissegundos | `150.2` |
| `generation_latency_ms` | `float` | ✅ Sim | Latência da geração da resposta pelo LLM em milissegundos | `1100.3` |
| `prompt_tokens` | `integer` | ✅ Sim | Número estimado de tokens do prompt enviado ao LLM | `450` |
| `completion_tokens` | `integer` | ✅ Sim | Número estimado de tokens da resposta gerada | `120` |
| `estimated_cost_usd` | `float` | ✅ Sim | Custo estimado em USD (0.0 para Ollama local) | `0.0` |
| `top_k_used` | `integer` | ✅ Sim | Número de documentos recuperados (top_k) | `5` |
| `context_size_chars` | `integer` | ✅ Sim | Tamanho total do contexto em caracteres | `3500` |

#### GuardrailStatus (Status dos Guardrails)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `blocked` | `boolean` | ✅ Sim | Indica se a requisição foi bloqueada pelos guardrails | `false` |
| `reason` | `string \| null` | ❌ Não | Motivo do bloqueio (apenas presente se `blocked = true`) | `"Solicitação bloqueada por tentativa de extração de informações internas."` |

---

## Exemplos de Resposta

### Resposta de Sucesso (200 OK)

```json
{
  "answer": "O horário de funcionamento é de segunda a sexta, das 9h às 18h, e aos sábados das 10h às 14h.",
  "citations": [
    {
      "source": "horarios.pdf",
      "excerpt": "O estabelecimento funciona de segunda a sexta-feira, das 9h às 18h, e aos sábados das 10h às 14h.",
      "page": 3,
      "relevance_score": 0.92
    },
    {
      "source": "regulamento.pdf",
      "excerpt": "Conforme o regulamento interno, o horário de atendimento segue o padrão comercial...",
      "page": 15,
      "relevance_score": 0.78
    }
  ],
  "metrics": {
    "total_latency_ms": 1250.5,
    "retrieval_latency_ms": 150.2,
    "generation_latency_ms": 1100.3,
    "prompt_tokens": 450,
    "completion_tokens": 120,
    "estimated_cost_usd": 0.0,
    "top_k_used": 5,
    "context_size_chars": 3500
  },
  "guardrail_status": {
    "blocked": false,
    "reason": null
  },
  "timestamp": "2025-01-15T14:30:45.123456"
}
```

### Resposta Bloqueada pelos Guardrails (200 OK)

Quando uma requisição é bloqueada pelos guardrails, o sistema retorna status `200` mas com `answer = null` e `guardrail_status.blocked = true`:

```json
{
  "answer": null,
  "citations": [],
  "metrics": {
    "total_latency_ms": 10.0,
    "retrieval_latency_ms": 0.0,
    "generation_latency_ms": 0.0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "estimated_cost_usd": 0.0,
    "top_k_used": 5,
    "context_size_chars": 0
  },
  "guardrail_status": {
    "blocked": true,
    "reason": "Solicitação bloqueada por tentativa de extração de informações internas."
  },
  "timestamp": "2025-01-15T14:30:45.123456"
}
```

### Erro Interno (500 Internal Server Error)

```json
{
  "detail": "Erro ao processar a requisição: Connection timeout"
}
```

---

## Regras de Negócio

### Validações

1. **Campo `question`**:
   - Deve ser uma string não vazia
   - Máximo recomendado: 2000 caracteres (validação de guardrails)

2. **Campo `top_k`**:
   - Se não informado, usa o valor padrão configurado (`DEFAULT_TOP_K`, geralmente 5)
   - Deve ser um inteiro positivo
   - Recomendado: entre 3 e 10 para melhor qualidade/resposta

### Guardrails

O sistema possui múltiplas camadas de segurança que podem bloquear requisições:

1. **Validação Regex**: Detecta padrões conhecidos de prompt injection, dados sensíveis (CPF, cartões), etc.
2. **Validação LLM**: Usa um modelo de linguagem para analisar a intenção da pergunta e classificar como SAFE ou UNSAFE.

**Quando bloqueado:**
- `answer` será `null`
- `citations` será uma lista vazia
- `guardrail_status.blocked` será `true`
- `guardrail_status.reason` conterá o motivo do bloqueio
- Métricas de geração serão zeradas (não houve processamento)

### Citações

- As citações são ordenadas por relevância (score decrescente)
- Cada citação contém um trecho do documento (excerpt) truncado em ~500 caracteres
- O campo `page` pode ser `null` se o documento não tiver numeração de páginas

### Métricas

- Todas as latências são em **milissegundos** (ms)
- Tokens são estimados usando heurística (~4 caracteres por token)
- Custo é sempre `0.0` para Ollama local (modelo self-hosted)
- `top_k_used` reflete o valor realmente utilizado (pode ser diferente do solicitado se houver menos documentos disponíveis)

---

## Exemplo de Uso com cURL

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais são os principais serviços oferecidos?",
    "top_k": 5
  }'
```

---

## Documentação Interativa

A API expõe documentação interativa via Swagger UI:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

