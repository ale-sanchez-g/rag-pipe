from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class PublishState(str, Enum):
    DRAFT = "draft"
    EVALUATED = "evaluated"
    PUBLISHED = "published"


class EmbeddingConfig(BaseModel):
    model: str
    version: str


class ChunkingConfig(BaseModel):
    strategy: str
    size: int = Field(gt=0)
    overlap: int = Field(ge=0)


class QualityThresholds(BaseModel):
    faithfulness_min: float = 0.85
    context_precision_min: float = 0.75
    max_regression_pct: float = 2.0


class PackManifest(BaseModel):
    pack_id: str
    pack_version: str
    domain_description: str
    licence: str
    owner: str
    embedding: EmbeddingConfig
    chunking: ChunkingConfig
    quality_thresholds: QualityThresholds = QualityThresholds()


class ChunkMetadata(BaseModel):
    pack_id: str
    pack_version: str
    source_uri: str
    section_path: str
    ingested_at: datetime
    contributor_id: str
