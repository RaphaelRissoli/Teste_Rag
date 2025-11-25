from fastapi import APIRouter, HTTPException

from src.api.schemas import QueryRequest, QueryResponse
from src.services.qa_service import qa_service



qa_router = APIRouter(prefix="/v1", tags=["qa"])


@qa_router.post("/query", response_model=QueryResponse)
def query_endpoint(payload: QueryRequest) -> QueryResponse:
    """
    Endpoint único de pergunta e resposta (Q&A).

    Regras de negócio principais:
    - Entrada: texto de pergunta (e opcionalmente top_k).
    - Saída: answer, citations, metrics, guardrail_status.
    """
    try:
        return qa_service.handle_query(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
