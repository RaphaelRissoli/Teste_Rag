from typing import List

from langchain_core.documents import Document

from src.core.config import settings
from src.clients.vector_store_client import get_vector_store_client, VectorStoreClient


class RetrievalClient:
    """
    Camada de alto nível para recuperação de documentos.
    Abstracao de Vector Store.
    """

    def __init__(self, client: VectorStoreClient | None = None) -> None:
        self._client = client or get_vector_store_client()

    def retrieve(self, query: str, top_k: int | None = None) -> List[Document]:
        """
        Recupera documentos relevantes para a query.
        """
        k = top_k or settings.DEFAULT_TOP_K
        return self._client.retrieve(query, k=k)

    def retriever(self, top_k: int | None = None):
        """
        Expoe um retriever LangChain para ser usado em chains mais elaboradas.
        """
        k = top_k or settings.DEFAULT_TOP_K
        return self._client.retriever(k=k)


# Instância singleton, compatível com o padrão anterior
retrieval_client = RetrievalClient()