
from typing import Iterable, List
from functools import lru_cache

from src.providers.embedding_provider import EmbeddingProvider
from src.core.embeddings_config import EmbeddingsConfig
from src.providers.ollama_embedding_provider import OllamaEmbeddingProvider



class EmbeddingsClient:
    """
    Client para embeddings.
    Tira a dependência de qual modelo de embedding estamos usando.
    """

    def __init__(self, provider: EmbeddingProvider) -> None:
        self._provider = provider

    def embed_query(self, text: str) -> List[float]:
        return self._provider.embed_query(text)

    def embed_documents(self, texts: Iterable[str]) -> List[List[float]]:
        return self._provider.embed_documents(texts)

    @property
    def as_langchain_embeddings(self):
        """
        Para passar direto para VectorStores (Qdrant, etc.).
        """
        return self._provider.langchain_embeddings


def _build_provider_from_env() -> EmbeddingProvider:
    """
    Factory que decide qual provider usar, baseada em config/env.
    Adiciona novos providers sem tocar no client.
    """
    import os

    backend = os.getenv("EMBEDDING_BACKEND", "ollama").lower()

    if backend == "ollama":
        cfg = EmbeddingsConfig()
        return OllamaEmbeddingProvider(cfg)

    raise ValueError(f"Backend de embedding não suportado: {backend}")


@lru_cache(maxsize=1)
def get_embeddings_client() -> EmbeddingsClient:
    """
    Singleton leve: uma instância por processo.
    """
    provider = _build_provider_from_env()
    return EmbeddingsClient(provider)