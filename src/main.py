from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from fastapi import FastAPI

from src.api.routes import router as api_router
from src.core.config import settings
from src.utils.logger import logger

logger.info("Inicializando Micro-RAG API...")

app = FastAPI(
    title="Micro-RAG API",
    description="API de Q&A com RAG sobre documentos indexados em Qdrant e LLM Ollama",
    version="1.0.0",
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
