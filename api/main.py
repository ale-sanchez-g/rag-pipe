from typing import Annotated
from fastapi import Depends, FastAPI
from api.auth import CustomerContext, require_customer, require_pack_access
from retrieval.contracts import RetrievalQuery, RetrievalResponse
from retrieval.service import RetrievalService

app = FastAPI(
    title="rag-pipe API",
    version="0.1.0",
    description=(
        "Multi-tenant, pack-versioned retrieval API for productised RAG "
        "knowledge packs. Use the **Authorize** button below to set your "
        "`x-api-key`, then try the endpoints directly from this page.\n\n"
        "Interactive docs: `/docs` (Swagger UI, this page) and `/redoc` "
        "(ReDoc). Machine-readable schema: `/openapi.json`."
    ),
)
service = RetrievalService()


@app.get(
    "/health",
    tags=["ops"],
    summary="Liveness check",
    description="Unauthenticated liveness probe used by orchestrators and smoke tests.",
)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/v1/packs/{pack_id}/query",
    response_model=RetrievalResponse,
    tags=["retrieval"],
    summary="Query a knowledge pack",
    description=(
        "Retrieves the top-k passages for a query within a single pack, "
        "scoped to the caller's entitlements. Requires a valid `x-api-key` "
        "for a customer entitled to `pack_id`."
    ),
    responses={
        401: {"description": "Missing or invalid API key"},
        403: {"description": "Caller is not entitled to this pack"},
    },
)
async def query_pack(
    pack_id: str,
    body: RetrievalQuery,
    customer: Annotated[CustomerContext, Depends(require_customer)],
) -> RetrievalResponse:
    require_pack_access(customer, pack_id)
    return service.query_pack(pack_id=pack_id, query=body)
