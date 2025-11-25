from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.clients.embedding_client import get_embeddings_client
from src.core.vector_store_config import VectorStoreConfig

def main() -> None:
    cfg = VectorStoreConfig()
    client = QdrantClient(url=cfg.url)

    # descobre o tamanho do vetor a partir do modelo de embedding
    emb_client = get_embeddings_client()
    dim = len(emb_client.embed_query("test"))

    # cria a collection se não existir
    if cfg.collection_name not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            collection_name=cfg.collection_name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        print(f"Collection {cfg.collection_name!r} criada com dim={dim}.")
    else:
        print(f"Collection {cfg.collection_name!r} já existe.")

if __name__ == "__main__":
    main()