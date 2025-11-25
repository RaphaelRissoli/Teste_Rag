from __future__ import annotations

import time

from langchain_ollama import ChatOllama
from langfuse.decorators import observe

from src.api.schemas import (
    GuardrailStatus,
    Metrics,
    QueryRequest,
    QueryResponse,
)
from src.clients.retrieval_client import retrieval_client
from src.core.config import settings
from src.providers.langfuse_provider import langfuse_provider
from src.utils.rag_helpers import build_citations, build_context, estimate_tokens


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

    @observe(name="handle_query")
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
        # Busca prompts (Langfuse ou Local via provider)
        sys_prompt_txt, rag_prompt_txt = langfuse_provider.get_prompts()
        print(sys_prompt_txt)
        print(rag_prompt_txt)
        contexto = build_context(docs)
        
        # Formata o prompt RAG
        # O provider já garante que temos strings, mas verificamos placeholders
        if "{contexto}" in rag_prompt_txt and "{question}" in rag_prompt_txt:
            prompt_rag = rag_prompt_txt.replace("{contexto}", contexto).replace("{question}", request.question)
        else:
            # Fallback se placeholders estiverem errados no prompt remoto
            # Poderíamos logar um aviso aqui
            # Tenta formatar mesmo assim ou usa uma string básica
            prompt_rag = f"Contexto:\n{contexto}\n\nPergunta: {request.question}"

        # Opcionalmente ancorar em um system prompt
        sys_txt = sys_prompt_txt.strip()
        full_prompt = f"{sys_txt}\n\n{prompt_rag}"

        # 4. Geração com LLM
        inicio_geracao = time.monotonic()
        
        # Configura callbacks do Langfuse para este invoke
        callbacks = []
        handler = langfuse_provider.get_callback_handler()
        if handler:
            callbacks.append(handler)

        resposta = self._llm.invoke(full_prompt, config={"callbacks": callbacks})
        fim_geracao = time.monotonic()
        generation_latency_ms = (fim_geracao - inicio_geracao) * 1000

        answer_text = resposta.content if hasattr(resposta, "content") else str(resposta)

        # 5. Métricas de tokens e custo
        prompt_tokens = estimate_tokens(full_prompt)
        completion_tokens = estimate_tokens(answer_text)
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
        citations = build_citations(docs)

        return QueryResponse(
            answer=answer_text,
            citations=citations,
            metrics=metrics,
            guardrail_status=guardrail_status,
        )


qa_service = QAService()
