import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenAI
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "llama3.2")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    
    # Qdrant
    VECTOR_DB_BACKEND: str = "qdrant"
    VECTOR_DB_URL: str = os.getenv("VECTOR_DB_URL", "http://localhost:6333")
    VECTOR_DB_COLLECTION_NAME: str = os.getenv("VECTOR_DB_COLLECTION_NAME", "rag_docs")
    
    # RAG Config
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    ENABLE_RERANKING: bool = os.getenv("ENABLE_RERANKING", "false").lower() == "true"
    
    # API Config
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Langfuse
    LANGFUSE_SECRET_KEY: str | None = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_PUBLIC_KEY: str | None = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

settings = Settings()