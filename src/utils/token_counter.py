import tiktoken
from core.config import settings

def count_tokens(text: str, model: str = None) -> int:
    """Conta tokens usando tiktoken"""
    model = model or settings.OPENAI_MODEL
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))