# Micro-RAG com Langfuse e Ollama

Projeto de RAG (Retrieval-Augmented Generation) utilizando:
- **FastAPI** para a API REST
- **Qdrant** como Vector Database
- **Ollama** para Embeddings e LLM (Llama 3.2)
- **Langfuse** para observabilidade e gestão de prompts

## Configuração

### 1. Variáveis de Ambiente
Crie um arquivo `.env` na raiz:

```env
# Langfuse (Opcional - para observabilidade)
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# RAG
CHUNK_SIZE=800
CHUNK_OVERLAP=200
DEFAULT_TOP_K=5

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 2. Instalação
```bash
uv sync
```

### 3. Execução
```bash
uv run src/main.py
```

## Langfuse: Gestão de Prompts

Para usar a gestão de prompts do Langfuse, crie dois prompts no painel do Langfuse com os seguintes nomes:

1. **`system-prompt`**: Prompt de sistema.
   - Exemplo: `Você é um assistente especialista em análise de documentos.`

2. **`rag-prompt`**: Template do prompt RAG.
   - Deve conter as variáveis `{{contexto}}` e `{{question}}`.
   - Exemplo:
     ```text
     Use o seguinte contexto para responder à pergunta.
     
     Contexto:
     {{contexto}}
     
     Pergunta: {{question}}
     ```

Se o Langfuse não estiver configurado ou falhar, o sistema usará automaticamente os prompts locais de fallback.

