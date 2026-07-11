import time
from math import ceil
import os

import pytest

from retrieval.contracts import RetrievalQuery
from retrieval.service import RetrievalService

pytestmark = pytest.mark.performance

NUM_SAMPLES = int(os.getenv("RAG_PIPE_PERF_SAMPLES", "50"))
P95_LATENCY_THRESHOLD_SECONDS = float(os.getenv("RAG_PIPE_PERF_P95_SECONDS", "0.5"))


def test_retrieval_service_p95_latency_smoke() -> None:
    service = RetrievalService()
    durations = []

    for _ in range(NUM_SAMPLES):
        start = time.perf_counter()
        result = service.query_pack(
            pack_id="threat-modelling-aws-war",
            query=RetrievalQuery(query="Summarise STRIDE", top_k=1),
        )
        durations.append(time.perf_counter() - start)
        assert result.results

    p95_index = max(ceil(len(durations) * 0.95) - 1, 0)
    p95 = sorted(durations)[p95_index]
    assert p95 < P95_LATENCY_THRESHOLD_SECONDS
