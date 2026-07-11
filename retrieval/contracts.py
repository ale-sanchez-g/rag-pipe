from pydantic import BaseModel, Field


class RetrievalQuery(BaseModel):
    query: str = Field(min_length=1, examples=["What is STRIDE?"])
    pack_version: str | None = Field(
        default=None,
        description="Pin to a specific published pack version; omit to use the latest.",
        examples=[None],
    )
    top_k: int = Field(default=5, ge=1, le=50)
    rerank: bool = False


class RetrievedPassage(BaseModel):
    chunk_id: str
    text: str
    score: float
    source_uri: str
    section_path: str


class RetrievalResponse(BaseModel):
    query_id: str
    pack_id: str
    pack_version: str
    results: list[RetrievedPassage]
