
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala uv via pip
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

# Instala dependências do projeto usando uv
RUN uv sync --frozen --no-dev


COPY src/ ./src/
COPY scripts/ ./scripts/
COPY data/ ./data/

COPY pytest.ini ./

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    OLLAMA_BASE_URL=http://ollama:11434 \
    VECTOR_DB_URL=http://qdrant:6333 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    LOG_LEVEL=INFO


CMD ["uv", "run", "src/main.py"]