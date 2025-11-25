# src/clients/vector_store_client.py

from __future__ import annotations

from functools import lru_cache
from typing import List

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from src.providers.vector_store_provider import VectorStoreProvider
from src.providers.qdrant_vector_store_provider import QdrantVectorStoreProvider
from src.core.vector_store_config import VectorStoreConfig
from src.clients.embedding_client import get_embeddings_client


class VectorStoreClient:
    """
    Fachada de alto nível para o Vector DB.
    Depende só da interface VectorStoreProvider.
    """

    def __init__(self, provider: VectorStoreProvider, k_default: int = 5) -> None:
        self._provider = provider
        self._k_default = k_default

    def index(self, documents: List[Document]) -> None:
        self._provider.index_documents(documents)

    def retrieve(self, query: str, k: int | None = None) -> List[Document]:
        k = k or self._k_default
        return self._provider.similarity_search(query, k=k)

    def retriever(self, k: int | None = None) -> VectorStoreRetriever:
        k = k or self._k_default
        return self._provider.as_retriever(k=k)


def _build_provider_from_env() -> VectorStoreProvider:
    """
    Factory de provider de Vector DB.
    Open/Closed: adicionar novos providers sem mexer no client.
    """
    config = VectorStoreConfig()
    backend = config.backend.lower()

    emb_client = get_embeddings_client()

    if backend == "qdrant":
        return QdrantVectorStoreProvider(config=config, embeddings_client=emb_client)

    raise ValueError(f"VECTOR_DB_BACKEND não suportado: {backend}")


@lru_cache(maxsize=1)
def get_vector_store_client() -> VectorStoreClient:
    provider = _build_provider_from_env()
    return VectorStoreClient(provider)