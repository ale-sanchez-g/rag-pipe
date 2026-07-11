from pydantic import BaseModel
from retrieval.contracts import RetrievalQuery, RetrievalResponse
from retrieval.service import RetrievalService


class MCPQueryInput(BaseModel):
    pack_id: str
    query: str
    pack_version: str | None = None
    top_k: int = 5
    rerank: bool = False


class MCPServer:
    def __init__(self) -> None:
        self.retrieval = RetrievalService()

    def query_pack(self, request: MCPQueryInput) -> RetrievalResponse:
        return self.retrieval.query_pack(
            pack_id=request.pack_id,
            query=RetrievalQuery(
                query=request.query,
                pack_version=request.pack_version,
                top_k=request.top_k,
                rerank=request.rerank,
            ),
        )
