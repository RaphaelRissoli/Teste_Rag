from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from core.config import settings


class ChunkingService:
    """
    Serviço responsável por fazer o chunking dos documentos.
    Não conhece embeddings nem vector DB, só texto + config.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self._chunk_size = chunk_size or settings.CHUNK_SIZE
        self._chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split(self, documents: List[Document]) -> List[Document]:
        """
        Divide documentos em chunks e adiciona metadata de índice.
        """
        chunks = self._splitter.split_documents(documents)

        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = idx

        return chunks

def chunk_documents(documents: List[Document]) -> List[Document]:
    return ChunkingService().split(documents)