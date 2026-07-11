import pytest

from mcp.server import MCPServer, MCPQueryInput

pytestmark = pytest.mark.unit


def test_mcp_server_query_pack_delegates_to_retrieval_service() -> None:
    server = MCPServer()
    response = server.query_pack(
        MCPQueryInput(
            pack_id="threat-modelling-aws-war", query="What is STRIDE?", top_k=1
        )
    )
    assert response.pack_id == "threat-modelling-aws-war"
    assert len(response.results) == 1


def test_mcp_query_input_defaults() -> None:
    request = MCPQueryInput(pack_id="threat-modelling-aws-war", query="What is STRIDE?")
    assert request.top_k == 5
    assert request.rerank is False
    assert request.pack_version is None
