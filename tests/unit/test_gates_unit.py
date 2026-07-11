from datetime import datetime, timezone

import pytest

from evaluation.contracts import RagasScores
from evaluation.gates import (
    duplication_gate,
    grounding_gate,
    regression_gate,
    schema_gate,
)
from ingestion.contracts import (
    ChunkMetadata,
    ChunkingConfig,
    EmbeddingConfig,
    PackManifest,
    QualityThresholds,
)

pytestmark = pytest.mark.unit


def manifest() -> PackManifest:
    return PackManifest(
        pack_id="threat-modelling-aws-war",
        pack_version="1.0.0",
        domain_description="desc",
        licence="MIT",
        owner="owner",
        embedding=EmbeddingConfig(model="BAAI/bge-large-en-v1.5", version="1.5"),
        chunking=ChunkingConfig(strategy="semantic", size=800, overlap=120),
        quality_thresholds=QualityThresholds(
            faithfulness_min=0.85, context_precision_min=0.75, max_regression_pct=2.0
        ),
    )


def test_schema_gate_passes_with_complete_metadata() -> None:
    chunk = ChunkMetadata(
        pack_id="threat-modelling-aws-war",
        pack_version="1.0.0",
        source_uri="doc.md",
        section_path="/",
        ingested_at=datetime.now(timezone.utc),
        contributor_id="alice",
    )
    assert schema_gate(manifest(), [chunk])


def test_grounding_gate_passes_thresholds() -> None:
    assert grounding_gate(
        RagasScores(
            faithfulness=0.9,
            context_precision=0.8,
            context_recall=0.7,
            answer_relevancy=0.8,
        ),
        manifest(),
    )


def test_regression_gate_fails_when_over_budget() -> None:
    assert not regression_gate(
        previous=RagasScores(
            faithfulness=0.9,
            context_precision=0.8,
            context_recall=0.7,
            answer_relevancy=0.8,
        ),
        current=RagasScores(
            faithfulness=0.86,
            context_precision=0.76,
            context_recall=0.7,
            answer_relevancy=0.8,
        ),
        max_regression_pct=2.0,
    )


def test_duplication_gate_threshold_behaviour() -> None:
    assert duplication_gate([0.2, 0.8, 0.97], threshold=0.97)
    assert not duplication_gate([0.2, 0.98], threshold=0.97)
