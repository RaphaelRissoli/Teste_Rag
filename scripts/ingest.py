
from src.clients.vector_store_client import get_vector_store_client
from src.ingestion.document_loader import load_documents
from src.ingestion.chunking import chunk_documents


def main():
    docs = load_documents()
    chunks = chunk_documents(docs)

    vs_client = get_vector_store_client()
    vs_client.index(chunks)

    print("Indexação concluída.")


if __name__ == "__main__":
    main()