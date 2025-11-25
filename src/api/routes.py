from fastapi import APIRouter

from src.api.v1.query_api import qa_router


router = APIRouter(prefix="/api")

router.include_router(qa_router)


@router.get("/health")
async def health_check() -> dict:
    """Endpoint simples de health-check."""
    return {"status": "healthy"}


@router.get("/")
async def root() -> dict:
    """Endpoint raiz com informações básicas da API."""
    return {
        "message": "Micro-RAG API",
        "version": "1.0.0",
        "docs": "/docs",
    }