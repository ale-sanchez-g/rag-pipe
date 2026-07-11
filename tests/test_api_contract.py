from fastapi.testclient import TestClient
from api.main import app


def test_query_requires_api_key() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/packs/threat-modelling-aws-war/query",
        json={"query": "What is STRIDE?", "top_k": 1},
    )
    assert response.status_code == 401


def test_query_returns_contract_shape() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/packs/threat-modelling-aws-war/query",
        headers={"x-api-key": "demo-key"},
        json={"query": "What is STRIDE?", "top_k": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["pack_id"] == "threat-modelling-aws-war"
    assert "query_id" in body
    assert body["results"]
    first = body["results"][0]
    assert {"chunk_id", "text", "score", "source_uri", "section_path"}.issubset(first.keys())
