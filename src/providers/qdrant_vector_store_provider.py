# src/providers/qdrant_vector_store_provider.py

from typing import List

from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from qdrant_client import QdrantClient

from src.providers.vector_store_provider import VectorStoreProvider
from src.core.vector_store_config import VectorStoreConfig
from src.clients.embedding_client import EmbeddingsClient 


class QdrantVectorStoreProvider(VectorStoreProvider):
    def __init__(
        self,
        config: VectorStoreConfig,
        embeddings_client: EmbeddingsClient,
    ) -> None:
        self._config = config
        self._emb_client = embeddings_client

        self._client = QdrantClient(url=config.url)
        self._vs = Qdrant(
            client=self._client,
            collection_name=config.collection_name,
            embeddings=self._emb_client.as_langchain_embeddings,
        )

    def index_documents(self, documents: List[Document]) -> None:
        """
        Adiciona documentos no índice.
        """
        self._vs.add_documents(documents)

    def similarity_search(self, query: str, k: int) -> List[Document]:
        return self._vs.similarity_search(query=query, k=k)

    def as_retriever(self, k: int) -> VectorStoreRetriever:
        return self._vs.as_retriever(search_kwargs={"k": k})