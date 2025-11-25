

from pydantic import BaseModel

from src.core.config import settings


class EmbeddingsConfig(BaseModel):
    model: str = settings.OLLAMA_EMBEDDING_MODEL
    base_url: str = settings.OLLAMA_BASE_URL
    timeout: int = 30
    batch_size: int = 16