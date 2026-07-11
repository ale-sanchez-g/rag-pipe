import time

import pytest

from retrieval.contracts import RetrievalQuery
from retrieval.service import RetrievalService

pytestmark = pytest.mark.performance


def test_retrieval_service_p95_latency_smoke() -> None:
    service = RetrievalService()
    durations = []

    for _ in range(50):
        start = time.perf_counter()
        result = service.query_pack(
            pack_id="threat-modelling-aws-war",
            query=RetrievalQuery(query="Summarise STRIDE", top_k=1),
        )
        durations.append(time.perf_counter() - start)
        assert result.results

    p95_index = max(int(len(durations) * 0.95) - 1, 0)
    p95 = sorted(durations)[p95_index]
    assert p95 < 0.05
