# src/core/vector_store_config.py

from pydantic import BaseModel

from src.core.config import settings


class VectorStoreConfig(BaseModel):
    backend: str = settings.VECTOR_DB_BACKEND
    url: str = settings.VECTOR_DB_URL
    collection_name: str = settings.VECTOR_DB_COLLECTION_NAME
    prefer_grpc: bool = False