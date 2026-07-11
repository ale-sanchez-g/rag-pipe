import os
from dataclasses import dataclass
from fastapi import Header, HTTPException, status


@dataclass
class CustomerContext:
    api_key: str
    customer_id: str
    allowed_packs: set[str]


def _parse_keys() -> dict[str, CustomerContext]:
    raw = os.getenv("RAG_PIPE_API_KEYS", "")
    rows = [row.strip() for row in raw.split(",") if row.strip()]
    parsed: dict[str, CustomerContext] = {}
    for row in rows:
        try:
            key, customer_id, packs = row.split(":", 2)
        except ValueError:
            continue
        allowed = {p.strip() for p in packs.split("|") if p.strip()}
        parsed[key] = CustomerContext(
            api_key=key, customer_id=customer_id, allowed_packs=allowed
        )
    return parsed


async def require_customer(x_api_key: str = Header(default="")) -> CustomerContext:
    keys = _parse_keys()
    context = keys.get(x_api_key)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    return context


def require_pack_access(context: CustomerContext, pack_id: str) -> None:
    if pack_id not in context.allowed_packs:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Pack access denied"
        )
