import logging
from rich.logging import RichHandler
from src.core.config import settings

def setup_logger(name: str = "micro_rag") -> logging.Logger:
    """
    Configura e retorna um logger.
    Usa RichHandler para output formatado no console.
    """
    # Configuração básica do logging
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    return logger

# Instância singleton global
logger = setup_logger()

