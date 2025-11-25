
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever


class VectorStoreProvider(ABC):
    """
    Abstração de Vector DB.
    O sistema conversa só com isso, não com Qdrant/Chroma/etc.
    """

    @abstractmethod
    def index_documents(self, documents: List[Document]) -> None:
        """
        Indexa (adiciona) documentos no índice vetorial.
        Pode criar a coleção se ainda não existir.
        """
        ...

    @abstractmethod
    def similarity_search(self, query: str, k: int) -> List[Document]:
        """
        Busca semântica simples.
        """
        ...

    @abstractmethod
    def as_retriever(self, k: int) -> VectorStoreRetriever:
        """
        Exposição de um retriever LangChain (para chains mais elaboradas).
        """
        ...