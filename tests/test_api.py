from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app
from src.api.schemas import QueryResponse, Metrics, GuardrailStatus
from datetime import datetime

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_query_endpoint_success():
    metrics = Metrics(
        total_latency_ms=100.0, retrieval_latency_ms=50.0, generation_latency_ms=50.0,
        prompt_tokens=10, completion_tokens=10, estimated_cost_usd=0.0,
        top_k_used=3, context_size_chars=100
    )
    guardrail = GuardrailStatus(blocked=False, reason=None)
    mock_response = QueryResponse(
        answer="Resposta teste",
        citations=[],
        metrics=metrics,
        guardrail_status=guardrail,
        timestamp=datetime.now()
    )

    # Mockamos o método handle_query da instância qa_service importada no módulo da API
    with patch("src.api.v1.query_api.qa_service.handle_query", return_value=mock_response):
        response = client.post("/api/v1/query", json={"question": "Teste", "top_k": 3})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Resposta teste"
        assert data["metrics"]["total_latency_ms"] == 100.0

def test_query_endpoint_guardrail_blocked():
    # Simula bloqueio
    metrics = Metrics(
        total_latency_ms=10.0, retrieval_latency_ms=0.0, generation_latency_ms=0.0,
        prompt_tokens=0, completion_tokens=0, estimated_cost_usd=0.0,
        top_k_used=3, context_size_chars=0
    )
    guardrail = GuardrailStatus(blocked=True, reason="Conteúdo impróprio")
    mock_response = QueryResponse(
        answer=None,
        citations=[],
        metrics=metrics,
        guardrail_status=guardrail,
        timestamp=datetime.now()
    )

    with patch("src.api.v1.query_api.qa_service.handle_query", return_value=mock_response):
        response = client.post("/api/v1/query", json={"question": "Teste Bloqueio"})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] is None
        assert data["guardrail_status"]["blocked"] is True
        assert data["guardrail_status"]["reason"] == "Conteúdo impróprio"

def test_query_endpoint_exception():
    with patch("src.api.v1.query_api.qa_service.handle_query", side_effect=Exception("Erro catastrófico")):
        response = client.post("/api/v1/query", json={"question": "Teste Erro"})
        assert response.status_code == 500
        assert "Erro catastrófico" in response.json()["detail"]

