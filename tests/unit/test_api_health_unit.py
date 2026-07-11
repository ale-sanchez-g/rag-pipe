import pytest
from fastapi.testclient import TestClient

from api.main import app

pytestmark = pytest.mark.unit


def test_health_endpoint_reports_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
