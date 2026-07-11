from typing import Annotated
from fastapi import Depends, FastAPI
from api.auth import CustomerContext, require_customer, require_pack_access
from retrieval.contracts import RetrievalQuery, RetrievalResponse
from retrieval.service import RetrievalService

app = FastAPI(title="rag-pipe API", version="0.1.0")
service = RetrievalService()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/packs/{pack_id}/query", response_model=RetrievalResponse)
async def query_pack(
    pack_id: str,
    body: RetrievalQuery,
    customer: Annotated[CustomerContext, Depends(require_customer)],
) -> RetrievalResponse:
    require_pack_access(customer, pack_id)
    return service.query_pack(pack_id=pack_id, query=body)
