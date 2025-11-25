# Micro-RAG API com Guardrails

API de Q&A (Question & Answer) baseada em RAG (Retrieval-Augmented Generation) que permite fazer perguntas sobre documentos indexados em um vector database, com múltiplas camadas de segurança (guardrails) e observabilidade completa.

## 🎯 Visão Geral

Este projeto implementa uma API REST que expõe funcionalidades de RAG, permitindo:
- **Retrieval**: Buscar informações relevantes de documentos indexados no vector database
- **Generation**: Gerar respostas contextualizadas usando LLM
- **Guardrails**: Proteção contra prompt injection, dados sensíveis e conteúdo malicioso
- **Observabilidade**: Rastreamento de métricas, custos e versionamento de prompts via Langfuse

## 🛠️ Tecnologias

- **FastAPI** - Framework web para expor a API REST
- **Ollama** - LLM local (Llama 3.2) e embeddings (nomic-embed-text)
- **Qdrant** - Vector database para armazenar embeddings e documentos
- **Langfuse** - Observabilidade, tracing e versionamento de prompts
- **LangChain** - Orquestração de RAG (document loading, chunking, retrieval)
- **Pytest** - Framework de testes (cobertura mínima: 70%)

## 🏗️ Arquitetura e Princípios de Design

### Abstração de Providers

O projeto segue os princípios **SOLID**, especialmente:
- **Open/Closed Principle**: Novos providers podem ser adicionados sem modificar o código existente
- **Single Responsibility Principle**: Cada provider tem uma responsabilidade única

**Providers Disponíveis:**
- `EmbeddingProvider` - Abstração para modelos de embedding (Ollama, OpenAI, etc.)
- `VectorStoreProvider` - Abstração para vector databases (Qdrant, Pinecone, etc.)
- `LangfuseProvider` - Gerenciamento de observabilidade e prompts

### Sistema de Fallback

- **Prompts Locais**: Prompts versionados na pasta `src/prompts/` servem como fallback
- **Langfuse**: Versionamento principal via Langfuse Cloud (opcional)
- Se Langfuse não estiver disponível, o sistema usa automaticamente os prompts locais

## 📋 Pré-requisitos

- **Python 3.13+**
- **Docker** e **Docker Compose** (recomendado)
- **uv** - Gerenciador de pacotes Python (instalado automaticamente no Dockerfile)

## 🚀 Como Executar

### Opção 1: Com Docker (Recomendado)

1. **Inicie todos os serviços:**
   ```bash
   docker-compose up --build
   ```

2. **Baixe os modelos do Ollama:**
   ```bash
   docker exec -it ollama ollama pull llama3.2
   docker exec -it ollama ollama pull nomic-embed-text
   ```

3. **Inicialize a collection no Qdrant:**
   ```bash
   docker-compose exec api uv run python scripts/init_qdrant.py
   ```

4. **Ingira os documentos:**
   ```bash
   docker-compose exec api uv run python scripts/ingest.py
   ```

5. **Teste a API:**
   ```bash
   curl http://localhost:8000/api/health
   ```

### Opção 2: Sem Docker

1. **Instale as dependências:**
   ```bash
   uv sync
   ```

2. **Inicie o Qdrant:**
   ```bash
   docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
   ```

3. **Inicie o Ollama:**
   ```bash
   docker run -d -p 11434:11434 ollama/ollama:latest
   ```

4. **Baixe os modelos:**
   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

5. **Inicialize a collection:**
   ```bash
   uv run python scripts/init_qdrant.py
   ```

6. **Ingira os documentos:**
   ```bash
   uv run python scripts/ingest.py
   ```

7. **Inicie a API:**
   ```bash
   uv run src/main.py
   ```

## 📁 Estrutura do Projeto

```
.
├── src/
│   ├── api/              # Rotas e schemas da API
│   ├── clients/          # Clientes de alto nível (retrieval, embedding)
│   ├── core/             # Configurações e tipos
│   ├── ingestion/        # Carregamento e chunking de documentos
│   ├── providers/        # Abstrações de providers (Ollama, Qdrant, Langfuse)
│   ├── prompts/         # Prompts versionados (fallback local)
│   ├── services/        # Lógica de negócio (QA, Guardrails)
│   └── utils/           # Funções auxiliares
├── scripts/
│   ├── init_qdrant.py   # Cria collection no Qdrant
│   └── ingest.py        # Indexa documentos da pasta data/
├── tests/               # Testes automatizados
├── docs/                # Documentação (Arquitetura, Contratos, Testes)
├── data/                # Documentos para indexação
└── docker-compose.yml   # Orquestração de serviços
```

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (opcional):

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Qdrant
VECTOR_DB_URL=http://localhost:6333
VECTOR_DB_COLLECTION_NAME=rag_docs

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# RAG Config
CHUNK_SIZE=800
CHUNK_OVERLAP=200
DEFAULT_TOP_K=5

# Langfuse (Opcional)
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

## 📖 Uso da API

### Health Check

```bash
curl http://localhost:8000/api/health
```

### Fazer uma Pergunta

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual é o horário de funcionamento?",
    "top_k": 5
  }'
```

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testes

### Executar Todos os Testes

```bash
uv run pytest
```

### Executar com Cobertura

```bash
uv run pytest --cov=src --cov-report=html
```

### Executar Teste Específico

```bash
uv run pytest tests/test_guardrails.py
```

**Cobertura mínima:** 70% (configurado em `pytest.ini`)

## 📚 Documentação Adicional

- **[Arquitetura](docs/ARQUITETURA.md)** - Visão geral da arquitetura e fluxo do sistema
- **[Contratos](docs/CONTRATOS.md)** - Especificação completa da API
- **[Testes](docs/TESTES.md)** - Processo de testes e validação manual

## 🛡️ Guardrails

O sistema possui múltiplas camadas de segurança:

1. **Validação Regex**: Detecta padrões conhecidos de prompt injection e dados sensíveis
2. **Validação LLM**: Usa análise semântica para detectar intenção maliciosa

### Alteraçoes opcionais na camada de enviroments
#### Utilizado:
| Parâmetro | Valor Escolhido | Alternativas | Impacto |
|-----------|-----------------|--------------|---------|
| **Chunk Size** | 800 | 500 (menor contexto), 1200 (mais contexto) | 800 equilibra contexto e granularidade |
| **Overlap** | 200 (25%) | 100 (12.5%), 400 (50%) | 25% é padrão da indústria |
| **Top-k** | 5 | 3 (mais preciso), 10 (mais recall) | 5 balanceia precisão e cobertura |

### 📈 Resultados Observados

Com estes parâmetros, o sistema alcança:
- **Latência Total**: ~1.2-1.5s por requisição
- **Relevância**: Alta precisão nas respostas (chunks recuperados são pertinentes)
- **Cobertura**: Perguntas complexas são respondidas com múltiplas fontes
- **Tamanho do Índice**: ~N/800 × 1.25 chunks por documento (considerando overlap)

### 🎯 Quando Ajustar os Parâmetros

**Aumente o Chunk Size (1000-1200)** se:
- Documentos têm parágrafos muito longos
- Conceitos são complexos e precisam de mais contexto

**Diminua o Chunk Size (500-600)** se:
- Documentos são muito estruturados (listas, tabelas)
- Precisa de maior granularidade na busca

### Lembre-se para o Top-k é possíel alterar na própria requisicao 

**Aumente o Top-k (7-10)** se:
- Perguntas são muito abertas ou exploratórias
- Precisa de mais diversidade de fontes

**Diminua o Top-k (3)** se:
- Perguntas são muito específicas
- Latência é crítica

## 📊 Observabilidade

- **Logs Estruturados**: Logging com Rich para output formatado
- **Langfuse Tracing**: Rastreamento automático de requisições, métricas e custos
- **Métricas Detalhadas**: Latência, tokens, custos por requisição


## 📝 Licença

Este projeto é um teste técnico.

---

**Desenvolvido por Raphael Rissoli**
