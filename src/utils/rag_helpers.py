from __future__ import annotations

from typing import List

from langchain_core.documents import Document

from src.api.schemas import Citation


def estimate_tokens(text: str) -> int:
    """
    Estimativa simples de tokens baseada no tamanho do texto.

    Evitamos dependência forte de tokenizer específico (tiktoken, etc.)
    e usamos uma heurística razoável (~4 caracteres por token).
    """
    if not text:
        return 0
    # Heurística simples: 1 token ~ 4 caracteres
    return max(1, len(text) // 4)


def build_context(docs: List[Document]) -> str:
    partes: List[str] = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "desconhecido")
        page = doc.metadata.get("page")
        page_info = f" (página {page})" if page is not None else ""
        partes.append(
            f"[Documento {idx} - Fonte: {source}{page_info}]\n{doc.page_content}\n"
        )
    return "\n".join(partes)


def build_citations(docs: List[Document]) -> List[Citation]:
    citations: List[Citation] = []
    for doc in docs:
        source = doc.metadata.get("source", "desconhecido")
        page = doc.metadata.get("page")
        # LangChain + Qdrant nem sempre retornam score explícito;
        # mantemos 0.0 por padrão
        relevance_score = float(doc.metadata.get("score", 0.0))

        excerpt = doc.page_content
        if len(excerpt) > 500:  # noqa: PLR2004 - manter simples por enquanto
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


