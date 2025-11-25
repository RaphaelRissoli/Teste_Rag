from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

from langchain_ollama import ChatOllama
from langchain_core.documents import Document

from src.api.schemas import (
    Citation,
    GuardrailStatus,
    Metrics,
    QueryRequest,
    QueryResponse,
)
from src.clients.retrieval_client import retrieval_client
from src.core.config import settings
from src.prompts.prompt_rag import RAG_PROMPT
from src.prompts.system_prompt import SYSTEM_PROMPT


@dataclass
class _QAResult:
    answer: Optional[str]
    citations: List[Citation]
    metrics: Metrics
    guardrail_status: GuardrailStatus


def _estimate_tokens(text: str) -> int:
    """
    Estimativa simples de tokens baseada no tamanho do texto.

    Evitamos dependência forte de tokenizer específico (tiktoken, etc.)
    e usamos uma heurística razoável (~4 caracteres por token).
    """
    if not text:
        return 0
    # Heurística simples: 1 token ~ 4 caracteres
    return max(1, len(text) // 4)


def _build_context(docs: List[Document]) -> str:
    partes: List[str] = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "desconhecido")
        page = doc.metadata.get("page")
        page_info = f" (página {page})" if page is not None else ""
        partes.append(
            f"[Documento {idx} - Fonte: {source}{page_info}]\n{doc.page_content}\n"
        )
    return "\n".join(partes)


def _build_citations(docs: List[Document]) -> List[Citation]:
    citations: List[Citation] = []
    for doc in docs:
        source = doc.metadata.get("source", "desconhecido")
        page = doc.metadata.get("page")
        # LangChain + Qdrant nem sempre retornam score explícito;
        # mantemos 0.0 por padrão (pode ser aprimorado para similarity_search_with_score).
        relevance_score = float(doc.metadata.get("score", 0.0))

        excerpt = doc.page_content
        if len(excerpt) > 500:
            excerpt = excerpt[:500] + "..."

        citations.append(
            Citation(
                source=source,
                excerpt=excerpt,
                page=page,
                relevance_score=relevance_score,
            )
        )

    return citations


class QAService:
    """
    Serviço de alto nível para perguntas e respostas (RAG).

    Responsável por:
    - Orquestrar retrieval
    - Montar o prompt de RAG
    - Chamar o LLM (Ollama)
    - Calcular métricas de latência e tokens
    """

    def __init__(self) -> None:
        self._llm = ChatOllama(
            model=settings.OLLAMA_LLM_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.2,
        )

    def _run_guardrails(self, question: str) -> GuardrailStatus:
        """
        Guardrails básicos.

        Esta implementação é intencionalmente simples e sempre permite,
        mas a estrutura já está pronta para ser expandida (injeção, domínio, etc.).
        """
        # TODO: integrar com módulo de guardrails quando disponível.
        return GuardrailStatus(blocked=False, reason=None)

    def handle_query(self, request: QueryRequest) -> QueryResponse:
        inicio_total = time.monotonic()

        # 1. Guardrails
        guardrail_status = self._run_guardrails(request.question)
        if guardrail_status.blocked:
            metrics = Metrics(
                total_latency_ms=0.0,
                retrieval_latency_ms=0.0,
                generation_latency_ms=0.0,
                prompt_tokens=0,
                completion_tokens=0,
                estimated_cost_usd=0.0,
                top_k_used=request.top_k or settings.DEFAULT_TOP_K,
                context_size_chars=0,
            )
            return QueryResponse(
                answer=None,
                citations=[],
                metrics=metrics,
                guardrail_status=guardrail_status,
            )

        # 2. Retrieval
        top_k = request.top_k or settings.DEFAULT_TOP_K
        inicio_retrieval = time.monotonic()
        docs = retrieval_client.retrieve(request.question, top_k=top_k)
        fim_retrieval = time.monotonic()
        retrieval_latency_ms = (fim_retrieval - inicio_retrieval) * 1000

        # 3. Construção do contexto / prompt
        contexto = _build_context(docs)
        prompt_rag = RAG_PROMPT.format(contexto=contexto, question=request.question)

        # Opcionalmente ancorar em um system prompt
        full_prompt = f"{SYSTEM_PROMPT.strip()}\n\n{prompt_rag}"

        # 4. Geração com LLM
        inicio_geracao = time.monotonic()
        resposta = self._llm.invoke(full_prompt)
        fim_geracao = time.monotonic()
        generation_latency_ms = (fim_geracao - inicio_geracao) * 1000

        answer_text = resposta.content if hasattr(resposta, "content") else str(resposta)

        # 5. Métricas de tokens e custo
        prompt_tokens = _estimate_tokens(full_prompt)
        completion_tokens = _estimate_tokens(answer_text)
        # Como Ollama roda local, custo financeiro é efetivamente 0
        estimated_cost_usd = 0.0

        total_latency_ms = (time.monotonic() - inicio_total) * 1000

        metrics = Metrics(
            total_latency_ms=round(total_latency_ms, 2),
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            generation_latency_ms=round(generation_latency_ms, 2),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            estimated_cost_usd=estimated_cost_usd,
            top_k_used=top_k,
            context_size_chars=len(contexto),
        )

        # 6. Citações
        citations = _build_citations(docs)

        return QueryResponse(
            answer=answer_text,
            citations=citations,
            metrics=metrics,
            guardrail_status=guardrail_status,
        )


qa_service = QAService()


