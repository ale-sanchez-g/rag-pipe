from pathlib import Path
from uuid import uuid4

from ingestion.manifest import load_manifest
from retrieval.contracts import RetrievalQuery, RetrievalResponse, RetrievedPassage


class RetrievalService:
    def query_pack(self, pack_id: str, query: RetrievalQuery) -> RetrievalResponse:
        version = query.pack_version
        if version is None:
            manifest_path = Path("packs") / pack_id / "manifest.yaml"
            version = load_manifest(manifest_path).pack_version

        sample = RetrievedPassage(
            chunk_id="sample-1",
            text="Use STRIDE to identify spoofing, tampering, repudiation, information disclosure, denial of service, and elevation of privilege risks in AWS workloads.",
            score=0.87,
            source_uri="packs/threat-modelling-aws-war/docs/stride-overview.md",
            section_path="/stride/overview",
        )
        return RetrievalResponse(
            query_id=str(uuid4()),
            pack_id=pack_id,
            pack_version=version,
            results=[sample][: query.top_k],
        )
