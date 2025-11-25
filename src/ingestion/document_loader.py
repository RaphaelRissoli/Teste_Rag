from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from typing import List

def load_documents(data_dir: str = "data") -> List[Document]:
    """Carrega todos os documentos da pasta data"""
    data_path = Path(data_dir)
    documents = []
    
    for file_path in sorted(data_path.glob("*")):
        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
            # Adicionar metadata com nome do arquivo
            for doc in docs:
                doc.metadata["source"] = file_path.name
            documents.extend(docs)
        elif file_path.suffix.lower() == ".txt":
            loader = TextLoader(str(file_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = file_path.name
            documents.extend(docs)
    
    return documents