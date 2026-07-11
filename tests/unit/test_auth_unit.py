import asyncio

import pytest
from fastapi import HTTPException

from api.auth import CustomerContext, require_customer, require_pack_access

pytestmark = pytest.mark.unit


def test_require_customer_resolves_context_for_known_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "RAG_PIPE_API_KEYS", "demo-key:customer-demo:pack-a|pack-b,other:cust-2:pack-c"
    )
    context = asyncio.run(require_customer(x_api_key="demo-key"))
    assert context == CustomerContext(
        api_key="demo-key",
        customer_id="customer-demo",
        allowed_packs={"pack-a", "pack-b"},
    )


def test_require_customer_rejects_unknown_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAG_PIPE_API_KEYS", "demo-key:customer-demo:pack-a")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_customer(x_api_key="missing-key"))
    assert exc_info.value.status_code == 401


def test_require_customer_ignores_malformed_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "RAG_PIPE_API_KEYS", "malformed-row,demo-key:customer-demo:pack-a"
    )
    context = asyncio.run(require_customer(x_api_key="demo-key"))
    assert context.customer_id == "customer-demo"


def test_require_pack_access_allows_entitled_pack() -> None:
    context = CustomerContext(
        api_key="demo-key", customer_id="customer-demo", allowed_packs={"pack-a"}
    )
    require_pack_access(context, "pack-a")


def test_require_pack_access_denies_unentitled_pack() -> None:
    context = CustomerContext(
        api_key="demo-key", customer_id="customer-demo", allowed_packs={"pack-a"}
    )
    with pytest.raises(HTTPException) as exc_info:
        require_pack_access(context, "pack-b")
    assert exc_info.value.status_code == 403
