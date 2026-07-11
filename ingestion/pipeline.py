from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from ingestion.contracts import ChunkMetadata, PackManifest


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".html", ".htm", ".docx"}


def discover_documents(path: Path) -> list[Path]:
    return [
        p
        for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def build_chunk_metadata(
    manifest: PackManifest, source_uri: str, section_path: str, contributor_id: str
) -> ChunkMetadata:
    return ChunkMetadata(
        pack_id=manifest.pack_id,
        pack_version=manifest.pack_version,
        source_uri=source_uri,
        section_path=section_path,
        ingested_at=datetime.now(timezone.utc),
        contributor_id=contributor_id,
    )


def ingest_documents(
    manifest: PackManifest, docs: Iterable[Path], contributor_id: str
) -> list[ChunkMetadata]:
    chunks = []
    for doc in docs:
        chunks.append(
            build_chunk_metadata(
                manifest=manifest,
                source_uri=str(doc),
                section_path="/",
                contributor_id=contributor_id,
            )
        )
    return chunks
