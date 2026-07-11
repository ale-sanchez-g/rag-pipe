from pathlib import Path

import pytest

from ingestion.contracts import (
    ChunkingConfig,
    EmbeddingConfig,
    PackManifest,
    QualityThresholds,
)
from ingestion.pipeline import (
    build_chunk_metadata,
    discover_documents,
    ingest_documents,
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


def test_discover_documents_filters_supported_extensions(tmp_path: Path) -> None:
    (tmp_path / "doc.md").write_text("content", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("content", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "page.html").write_text("<p>content</p>", encoding="utf-8")

    docs = discover_documents(tmp_path)

    names = {doc.name for doc in docs}
    assert names == {"doc.md", "page.html"}


def test_build_chunk_metadata_populates_pack_fields() -> None:
    chunk = build_chunk_metadata(
        manifest=manifest(),
        source_uri="doc.md",
        section_path="/intro",
        contributor_id="alice",
    )
    assert chunk.pack_id == "threat-modelling-aws-war"
    assert chunk.section_path == "/intro"
    assert chunk.contributor_id == "alice"


def test_ingest_documents_builds_one_chunk_per_document(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text("content", encoding="utf-8")

    chunks = ingest_documents(manifest=manifest(), docs=[doc], contributor_id="alice")

    assert len(chunks) == 1
    assert chunks[0].source_uri == str(doc)
