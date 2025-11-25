import pytest
from unittest.mock import MagicMock, patch
from src.services.qa_service import QAService
from src.api.schemas import QueryRequest, QueryResponse, GuardrailStatus

@pytest.fixture
def mock_dependencies():
    with patch("src.services.qa_service.ChatOllama") as mock_llm_cls, \
         patch("src.services.qa_service.retrieval_client") as mock_retrieval, \
         patch("src.services.qa_service.langfuse_provider") as mock_langfuse, \
         patch("src.services.qa_service.build_context") as mock_build_context, \
         patch("src.services.qa_service.build_citations") as mock_build_citations, \
         patch("src.services.qa_service.estimate_tokens") as mock_estimate_tokens:
        
        mock_llm_instance = MagicMock()
        mock_llm_cls.return_value = mock_llm_instance
        
        yield {
            "llm": mock_llm_instance,
            "retrieval": mock_retrieval,
            "langfuse": mock_langfuse,
            "build_context": mock_build_context,
            "build_citations": mock_build_citations,
            "estimate_tokens": mock_estimate_tokens
        }

def test_qa_service_handle_query_success(mock_dependencies):
    # Setup
    service = QAService()
    
    # Mock guardrails (internal method)
    service._run_guardrails = MagicMock(return_value=GuardrailStatus(blocked=False))
    
    # Mock dependencies return values
    mock_dependencies["retrieval"].retrieve.return_value = ["doc1"]
    mock_dependencies["langfuse"].get_prompts.return_value = ("SysPrompt", "RAGPrompt {contexto} {question}")
    mock_dependencies["langfuse"].get_callback_handler.return_value = None
    mock_dependencies["build_context"].return_value = "Contexto"
    
    mock_response = MagicMock()
    mock_response.content = "Resposta final"
    mock_dependencies["llm"].invoke.return_value = mock_response
    
    mock_dependencies["estimate_tokens"].return_value = 10
    mock_dependencies["build_citations"].return_value = []

    # Execute
    request = QueryRequest(question="Pergunta", top_k=5)
    response = service.handle_query(request)

    # Assert
    assert response.answer == "Resposta final"
    mock_dependencies["retrieval"].retrieve.assert_called_once_with("Pergunta", top_k=5)
    mock_dependencies["llm"].invoke.assert_called_once()

def test_qa_service_handle_query_blocked(mock_dependencies):
    service = QAService()
    service._run_guardrails = MagicMock(return_value=GuardrailStatus(blocked=True, reason="Blocked"))
    
    request = QueryRequest(question="Malicious", top_k=5)
    response = service.handle_query(request)
    
    assert response.answer is None
    assert response.guardrail_status.blocked is True
    mock_dependencies["llm"].invoke.assert_not_called()

