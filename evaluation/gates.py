from typing import Iterable
from evaluation.contracts import RagasScores
from ingestion.contracts import ChunkMetadata, PackManifest


def schema_gate(manifest: PackManifest, chunks: Iterable[ChunkMetadata]) -> bool:
    required_fields = {
        "pack_id",
        "pack_version",
        "source_uri",
        "section_path",
        "ingested_at",
        "contributor_id",
    }
    for chunk in chunks:
        data = chunk.model_dump()
        if not required_fields.issubset(data.keys()):
            return False
        if any(data.get(k) in (None, "") for k in required_fields):
            return False
    return True


def duplication_gate(similarities: Iterable[float], threshold: float = 0.97) -> bool:
    return all(score <= threshold for score in similarities)


def grounding_gate(scores: RagasScores, manifest: PackManifest) -> bool:
    return (
        scores.faithfulness >= manifest.quality_thresholds.faithfulness_min
        and scores.context_precision
        >= manifest.quality_thresholds.context_precision_min
    )


def regression_gate(
    previous: RagasScores, current: RagasScores, max_regression_pct: float
) -> bool:
    def within_budget(old: float, new: float) -> bool:
        if old <= 0:
            return True
        regression_pct = ((old - new) / old) * 100
        return regression_pct <= max_regression_pct

    return within_budget(previous.faithfulness, current.faithfulness) and within_budget(
        previous.context_precision, current.context_precision
    )
