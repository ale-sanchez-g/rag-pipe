from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

from evaluation.contracts import RagasScores
from evaluation.gates import grounding_gate, regression_gate, schema_gate
from ingestion.cli import app as ingest_app
from ingestion.contracts import (
    ChunkingConfig,
    ChunkMetadata,
    EmbeddingConfig,
    PackManifest,
    QualityThresholds,
)
from ingestion.manifest import load_manifest
from ingestion.pipeline import ingest_documents
from mcp.server import MCPQueryInput, MCPServer

pytestmark = pytest.mark.security

MANIFEST_YAML = """
pack_id: threat-modelling-aws-war
pack_version: "1.0.0"
domain_description: desc
licence: MIT
owner: owner
embedding:
  model: BAAI/bge-large-en-v1.5
  version: "1.5"
chunking:
  strategy: semantic
  size: 800
  overlap: 120
quality_thresholds:
  faithfulness_min: 0.85
  context_precision_min: 0.75
  max_regression_pct: 2.0
"""


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


def test_schema_gate_rejects_chunks_ingested_for_a_different_pack() -> None:
    foreign_chunk = ChunkMetadata(
        pack_id="another-tenant-pack",
        pack_version="1.0.0",
        source_uri="doc.md",
        section_path="/",
        ingested_at=datetime.now(timezone.utc),
        contributor_id="alice",
    )
    assert not schema_gate(manifest(), [foreign_chunk])


def test_load_manifest_round_trip_preserves_pack_identity(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text(MANIFEST_YAML, encoding="utf-8")

    loaded = load_manifest(manifest_path)

    assert loaded.pack_id == "threat-modelling-aws-war"


def test_ingest_cli_refuses_to_publish_content_under_wrong_pack_id(
    tmp_path: Path,
) -> None:
    (tmp_path / "manifest.yaml").write_text(MANIFEST_YAML, encoding="utf-8")
    (tmp_path / "doc.md").write_text("content", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(ingest_app, [str(tmp_path), "someone-elses-pack"])

    assert result.exit_code != 0


def test_ingest_documents_tags_chunks_with_the_source_pack_identity(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text("content", encoding="utf-8")

    chunks = ingest_documents(manifest=manifest(), docs=[doc], contributor_id="alice")

    assert all(chunk.pack_id == "threat-modelling-aws-war" for chunk in chunks)


def test_mcp_server_query_is_scoped_to_the_requested_pack() -> None:
    server = MCPServer()
    response = server.query_pack(
        MCPQueryInput(pack_id="threat-modelling-aws-war", query="What is STRIDE?")
    )
    assert response.pack_id == "threat-modelling-aws-war"


def test_grounding_gate_blocks_publish_below_quality_thresholds() -> None:
    assert not grounding_gate(
        RagasScores(
            faithfulness=0.5,
            context_precision=0.5,
            context_recall=0.5,
            answer_relevancy=0.5,
        ),
        manifest(),
    )


def test_regression_gate_blocks_publish_on_quality_regression() -> None:
    assert not regression_gate(
        previous=RagasScores(
            faithfulness=0.9,
            context_precision=0.9,
            context_recall=0.9,
            answer_relevancy=0.9,
        ),
        current=RagasScores(
            faithfulness=0.5,
            context_precision=0.5,
            context_recall=0.5,
            answer_relevancy=0.5,
        ),
        max_regression_pct=2.0,
    )
