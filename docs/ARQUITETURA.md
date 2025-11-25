# Arquitetura do RAG com Guardrails

## Visão Geral

Sistema de RAG que permite fazer perguntas sobre documentos indexados, com múltiplas camadas de segurança (guardrails) e observabilidade completa via Langfuse.

## Fluxo Arquitetural Principal

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FASE DE INGESTÃO                               │
└─────────────────────────────────────────────────────────────────────────┘

1. CARREGAMENTO DE DOCUMENTOS
   └─> src/ingestion/document_loader.py
       • Lê PDFs e TXTs da pasta `data/`
       • Extrai texto e metadados (nome do arquivo, página)

2. CHUNKING
   └─> src/ingestion/chunking.py
       • Divide documentos em chunks (tamanho: 800 chars, overlap: 200)
       • Adiciona metadados de índice

3. EMBEDDING
   └─> src/clients/embedding_client.py
       └─> OllamaEmbeddingProvider (nomic-embed-text)
           • Gera vetores de embedding para cada chunk

4. INDEXAÇÃO
   └─> src/clients/vector_store_client.py
       └─> QdrantVectorStoreProvider
           • Armazena chunks + embeddings no Qdrant
           • Collection: `rag_docs`


┌─────────────────────────────────────────────────────────────────────────┐
│                    FASE DE QUERY (RAG Pipeline)                         │
└─────────────────────────────────────────────────────────────────────────┘

5. RECEPÇÃO DA REQUISIÇÃO
   └─> FastAPI Endpoint: POST /api/v1/query
       └─> src/api/v1/query_api.py
           • Recebe: { "question": "...", "top_k": 3 }
           • Valida schema (QueryRequest)

6. GUARDRAILS (Primeira Camada)
   └─> src/services/guardrrails_service.py
       ├─> Validação Regex (rápida):
       │   • Padrões de prompt injection
       │   • Dados sensíveis (CPF, cartões)
       │   • Escalação de privilégios
       │
       └─> Validação LLM (análise de intenção):
           • Usa Ollama + Prompt de Guardrail
           • Classifica como SAFE ou UNSAFE
           • Se bloqueado → retorna resposta com reason

7. RETRIEVAL
   └─> src/clients/retrieval_client.py
       └─> VectorStoreClient.retrieve()
           • Gera embedding da pergunta (Ollama)
           • Busca similaridade no Qdrant (top_k documentos)
           • Retorna Document[] com metadados

8. COMPOSIÇÃO DE CONTEXTO
   └─> src/utils/rag_helpers.py::build_context()
       • Formata documentos recuperados
       • Adiciona metadados (fonte, página)
       • Estrutura: "[Documento N - Fonte: X (página Y)]\n{conteúdo}"

9. BUSCA DE PROMPTS (Versionados)
   └─> src/providers/langfuse_provider.py
       • Tenta buscar do Langfuse Cloud:
         - system-prompt
         - rag-prompt
         - guardrail-prompt
       • Fallback para prompts locais se falhar

10. MONTAGEM DO PROMPT FINAL
    └─> src/services/qa_service.py
        • Combina: System Prompt + RAG Prompt
        • Insere contexto e pergunta nos placeholders
        • Resultado: prompt completo para o LLM

11. GERAÇÃO (LLM)
    └─> ChatOllama (llama3.2)
        • Recebe prompt completo
        • Gera resposta baseada no contexto
        • Callback Langfuse captura tokens/latência

12. PÓS-PROCESSAMENTO
    └─> src/utils/rag_helpers.py
        ├─> build_citations(): Extrai citações dos documentos
        └─> estimate_tokens(): Calcula tokens (heurística)

13. MÉTRICAS
    └─> Calcula:
        • Latência total, retrieval, geração
        • Tokens (prompt + completion)
        • Custo estimado (0 para Ollama local)
        • Tamanho do contexto

14. RESPOSTA FINAL
    └─> QueryResponse
        • answer: texto gerado
        • citations: lista de fontes
        • metrics: métricas de execução
        • guardrail_status: status de segurança
        • timestamp: data/hora


┌─────────────────────────────────────────────────────────────────────────┐
│                    OBSERVABILIDADE & LOGGING                            │
└─────────────────────────────────────────────────────────────────────────┘

15. LOGGING ESTRUTURADO
    └─> src/utils/logger.py
        • RichHandler para output formatado
        • Níveis: DEBUG, INFO, WARNING, ERROR

16. TRACING (Langfuse)
    └─> @observe decorator no handle_query
        • Cria traces automáticos
        • Captura inputs/outputs
        • Métricas de latência e tokens
        • Dashboard em cloud.langfuse.com


┌─────────────────────────────────────────────────────────────────────────┐
│                        COMPONENTES PRINCIPAIS                           │
└─────────────────────────────────────────────────────────────────────────┘

📁 src/api/
   ├─ routes.py          → Router raiz da API (/api)
   ├─ schemas.py         → Pydantic models (Request/Response)
   └─ v1/query_api.py    → Endpoint de Q&A (/api/v1/query)

📁 src/services/
   ├─ qa_service.py           → Orquestrador principal do RAG
   └─ guardrrails_service.py  → Validação de segurança (regex + LLM)

📁 src/clients/
   ├─ retrieval_client.py      → Abstração de retrieval
   ├─ embedding_client.py      → Abstração de embeddings
   └─ vector_store_client.py   → Abstração de vector DB

📁 src/providers/
   ├─ langfuse_provider.py          → Integração Langfuse (prompts + tracing)
   ├─ embedding_provider.py         → Interface de embeddings
   ├─ ollama_embedding_provider.py  → Implementação Ollama
   ├─ vector_store_provider.py      → Interface de vector store
   └─ qdrant_vector_store_provider.py → Implementação Qdrant

📁 src/utils/
   ├─ rag_helpers.py  → Funções auxiliares (context, citations, tokens)
   └─ logger.py       → Configuração de logging

📁 src/prompts/
   ├─ system_prompt/v1/     → Prompt de sistema (persona)
   ├─ rag_prompt/V1/        → Template do prompt RAG
   └─ guardrrails/v1/       → Prompt para validação LLM


┌─────────────────────────────────────────────────────────────────────────┐
│                        INTEGRAÇÕES EXTERNAS                            │
└─────────────────────────────────────────────────────────────────────────┘

🔵 Ollama (Local)
   • LLM: llama3.2 (geração de respostas)
   • Embeddings: nomic-embed-text (vetorização)
   • Base URL: http://localhost:11434

🟢 Qdrant (Vector Database)
   • Armazena embeddings e documentos
   • Busca por similaridade semântica
   • URL: http://localhost:6333
   • Collection: rag_docs

🟡 Langfuse Cloud (Observabilidade)
   • Gestão de prompts versionados
   • Tracing de requisições
   • Métricas e analytics
   • URL: https://cloud.langfuse.com


┌─────────────────────────────────────────────────────────────────────────┐
│                        CAMADAS DE SEGURANÇA                             │
└─────────────────────────────────────────────────────────────────────────┘

🛡️ Guardrails (Múltiplas Camadas)

1. Regex Patterns (Rápido)
   • Prompt injection conhecidos
   • Dados sensíveis (CPF, cartões)
   • Comandos de sistema

2. LLM Classifier (Análise Semântica)
   • Usa Ollama + Prompt de Guardrail
   • Detecta intenção maliciosa
   • Classifica: SAFE ou UNSAFE

3. Fail-Safe
   • Se LLM falhar → não bloqueia (fail-open)
   • Logs de erro para auditoria


┌─────────────────────────────────────────────────────────────────────────┐
│                        FLUXO DE DADOS RESUMIDO                          │
└─────────────────────────────────────────────────────────────────────────┘

Ingestão:
  Documentos → Chunking → Embeddings → Qdrant

Query:
  Pergunta → Guardrails → Embedding → Retrieval → Contexto → 
  Prompt → LLM → Resposta → Citações → Métricas → Response JSON

Observabilidade:
  Todas as etapas → Langfuse Tracing → Dashboard


┌─────────────────────────────────────────────────────────────────────────┐
│                        DECISÕES ARQUITETURAIS                           │
└─────────────────────────────────────────────────────────────────────────┘

✅ Separação de Responsabilidades
   • Providers: abstrações de serviços externos
   • Clients: fachadas de alto nível
   • Services: lógica de negócio
   • Utils: funções puras auxiliares

✅ Fallback Robusto
   • Prompts: Langfuse → Local
   • Guardrails: LLM → Regex apenas
   • Observabilidade: Langfuse opcional

✅ Testabilidade
   • Dependências injetáveis
   • Mocks fáceis de configurar
   • Cobertura de testes > 70%

✅ Observabilidade
   • Logging estruturado
   • Tracing automático (Langfuse)
   • Métricas detalhadas por requisição

