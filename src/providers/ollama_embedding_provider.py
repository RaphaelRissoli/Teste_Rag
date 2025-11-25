# src/rag/ollama_embedding_provider.py

from typing import Iterable, List
from langchain_ollama import OllamaEmbeddings

from providers.embedding_provider import EmbeddingProvider
from src.core.embeddings_config import EmbeddingsConfig  # já existe no seu projeto


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, config: EmbeddingsConfig) -> None:
        self._config = config
        self._lc = OllamaEmbeddings(
            model=config.model,
            base_url=config.base_url,
        )

    def embed_query(self, text: str) -> List[float]:
        return self._lc.embed_query(text)

    def embed_documents(self, texts: Iterable[str]) -> List[List[float]]:
        return self._lc.embed_documents(list(texts))

    @property
    def langchain_embeddings(self) -> OllamaEmbeddings:
        return self._lc