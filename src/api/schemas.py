from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class QueryRequest(BaseModel):
    question: str = Field(..., description="Pergunta do usuário")
    top_k: Optional[int] = Field(None, description="Número de documentos a recuperar (opcional)")

class Citation(BaseModel):
    source: str = Field(..., description="Nome do documento fonte")
    excerpt: str = Field(..., description="Trecho relevante do documento")
    page: Optional[int] = Field(None, description="Número da página (se aplicável)")
    relevance_score: float = Field(..., description="Score de relevância (0-1)")

class Metrics(BaseModel):
    total_latency_ms: float = Field(..., description="Latência total em milissegundos")
    retrieval_latency_ms: float = Field(..., description="Latência do retrieval em milissegundos")
    generation_latency_ms: float = Field(..., description="Latência da geração em milissegundos")
    prompt_tokens: int = Field(..., description="Número de tokens do prompt")
    completion_tokens: int = Field(..., description="Número de tokens da resposta")
    estimated_cost_usd: float = Field(..., description="Custo estimado em USD")
    top_k_used: int = Field(..., description="Top-K utilizado na busca")
    context_size_chars: int = Field(..., description="Tamanho do contexto em caracteres")

class GuardrailStatus(BaseModel):
    blocked: bool = Field(..., description="Indica se a requisição foi bloqueada")
    reason: Optional[str] = Field(None, description="Motivo do bloqueio (se aplicável)")

class QueryResponse(BaseModel):
    answer: Optional[str] = Field(None, description="Resposta gerada (null se bloqueado)")
    citations: List[Citation] = Field(default_factory=list, description="Lista de citações")
    metrics: Metrics = Field(..., description="Métricas de execução")
    guardrail_status: GuardrailStatus = Field(..., description="Status dos guardrails")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da requisição")