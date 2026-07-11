import pytest

from retrieval.contracts import RetrievalQuery, RetrievedPassage, RetrievalResponse
from retrieval.service import RetrievalService

pytestmark = pytest.mark.unit


def test_retrieval_query_defaults() -> None:
    query = RetrievalQuery(query="What is STRIDE?")
    assert query.top_k == 5
    assert query.rerank is False
    assert query.pack_version is None


def test_retrieval_response_round_trip() -> None:
    passage = RetrievedPassage(
        chunk_id="chunk-1",
        text="sample text",
        score=0.5,
        source_uri="doc.md",
        section_path="/",
    )
    response = RetrievalResponse(
        query_id="query-1",
        pack_id="threat-modelling-aws-war",
        pack_version="1.0.0",
        results=[passage],
    )
    assert response.results[0].chunk_id == "chunk-1"


def test_retrieval_service_returns_requested_pack_and_version() -> None:
    service = RetrievalService()
    result = service.query_pack(
        pack_id="threat-modelling-aws-war",
        query=RetrievalQuery(query="What is STRIDE?", pack_version="2.0.0", top_k=1),
    )
    assert result.pack_id == "threat-modelling-aws-war"
    assert result.pack_version == "2.0.0"
    assert len(result.results) == 1


def test_retrieval_service_resolves_version_from_pack_manifest_when_omitted() -> None:
    service = RetrievalService()
    result = service.query_pack(
        pack_id="threat-modelling-aws-war",
        query=RetrievalQuery(query="What is STRIDE?"),
    )
    assert result.pack_version == "1.0.0"
