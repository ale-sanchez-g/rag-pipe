import pytest
from fastapi.testclient import TestClient

from api.main import app

pytestmark = pytest.mark.security


def test_query_is_denied_for_unentitled_pack(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAG_PIPE_API_KEYS", "demo-key:customer-demo:dora-metrics")
    client = TestClient(app)
    response = client.post(
        "/v1/packs/threat-modelling-aws-war/query",
        headers={"x-api-key": "demo-key"},
        json={"query": "What is STRIDE?", "top_k": 1},
    )

    assert response.status_code == 403
