# src/rag/embedding_provider.py

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, List
from langchain_core.embeddings import Embeddings as LCEmbeddings


class EmbeddingProvider(ABC):
    """
    Abstração de provider de embeddings.
    Qualquer backend (Ollama, OpenAI, etc.) implementa isso.
    """

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        ...

    @abstractmethod
    def embed_documents(self, texts: Iterable[str]) -> List[List[float]]:
        ...

    @property
    @abstractmethod
    def langchain_embeddings(self) -> LCEmbeddings:
        """
        Objeto compatível com LangChain para usar em VectorStore.
        """
        ...