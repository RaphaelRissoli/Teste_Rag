from typing import Optional, Tuple
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from src.core.config import settings
from src.prompts.rag_prompt.V1.prompt_rag import RAG_PROMPT as LOCAL_RAG_PROMPT
from src.prompts.system_prompt.v1.system_prompt import SYSTEM_PROMPT_V1 as LOCAL_SYSTEM_PROMPT
from src.prompts.guardrrails.v1.guardrrails_prompt import GUARDRAIL_PROMPT_V1 as LOCAL_GUARDRAIL_PROMPT

class LangfuseProvider:
    """
    Provider responsável pela integração com o Langfuse.
    Gerencia a inicialização do cliente, recuperação de prompts e callbacks.
    """

    def __init__(self) -> None:
        self._client: Optional[Langfuse] = None
        self._initialize()

    def _initialize(self) -> None:
        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            try:
                self._client = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
            except Exception:
                self._client = None

    @property
    def is_enabled(self) -> bool:
        return self._client is not None

    def get_callback_handler(self) -> Optional[CallbackHandler]:
        """Retorna um handler de callback para ser usado nas chains do LangChain."""
        if not self.is_enabled:
            return None
        
        return CallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )

    def get_prompts(self) -> Tuple[str, str]:
        """
        Retorna (system_prompt, rag_prompt).
        Tenta buscar do Langfuse; se falhar ou não estiver configurado, usa os locais.
        """
        sys_prompt = LOCAL_SYSTEM_PROMPT
        rag_prompt = LOCAL_RAG_PROMPT

        if self.is_enabled and self._client:
            try:
                lf_sys = self._client.get_prompt("system-prompt")
                lf_rag = self._client.get_prompt("rag-prompt")

                if lf_sys:
                    sys_prompt = lf_sys.get_langchain_prompt()
                if lf_rag:
                    rag_prompt = lf_rag.get_langchain_prompt()
            except Exception:
                # Fallback silencioso
                pass
        
        return str(sys_prompt), str(rag_prompt)

    def get_guardrail_prompt(self) -> str:
        """
        Retorna o prompt de guardrail.
        """
        prompt = LOCAL_GUARDRAIL_PROMPT

        if self.is_enabled and self._client:
            try:
                lf_prompt = self._client.get_prompt("guardrail-prompt")
                if lf_prompt:
                    prompt = lf_prompt.get_langchain_prompt()
            except Exception:
                pass
        
        return str(prompt)
langfuse_provider = LangfuseProvider()

