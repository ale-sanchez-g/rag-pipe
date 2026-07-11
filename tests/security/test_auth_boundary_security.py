import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.auth import require_customer

pytestmark = pytest.mark.security


def test_health_endpoint_requires_no_auth() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_query_succeeds_for_entitled_pack(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "RAG_PIPE_API_KEYS", "demo-key:customer-demo:threat-modelling-aws-war"
    )
    client = TestClient(app)
    response = client.post(
        "/v1/packs/threat-modelling-aws-war/query",
        headers={"x-api-key": "demo-key"},
        json={"query": "What is STRIDE?", "top_k": 1},
    )
    assert response.status_code == 200


def test_query_rejected_when_api_key_missing() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/packs/threat-modelling-aws-war/query",
        json={"query": "What is STRIDE?", "top_k": 1},
    )
    assert response.status_code == 401


def test_malformed_api_key_rows_are_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "RAG_PIPE_API_KEYS", "not-a-valid-row, ,demo-key:customer-demo:pack-a"
    )
    import asyncio

    context = asyncio.run(require_customer(x_api_key="demo-key"))
    assert context.customer_id == "customer-demo"
