"""End-to-end health/landing/MCP-init checks via Starlette TestClient."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient


@pytest.fixture(autouse=True)
def _disable_dns_protection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PY_DOCSBOX_DISABLE_DNS_PROTECTION", "1")


def _make_app():
    import httpx

    from python_docsbox_mcp.corpus import _EmptyCorpus
    from python_docsbox_mcp.server import _build_app, _build_mcp

    mcp = _build_mcp(_EmptyCorpus(), httpx.AsyncClient(), host="127.0.0.1", port=0)
    return _build_app(mcp)


def test_health_and_index() -> None:
    app = _make_app()

    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        r = client.get("/")
        assert r.status_code == 200
        assert "python-docsbox-mcp" in r.text


def test_mcp_initialize() -> None:
    app = _make_app()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0"},
        },
    }
    with TestClient(app) as client:
        r = client.post(
            "/mcp",
            json=payload,
            headers={"accept": "application/json, text/event-stream"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["result"]["serverInfo"]["name"] == "python-docsbox"
        assert "tools" in body["result"]["capabilities"]
