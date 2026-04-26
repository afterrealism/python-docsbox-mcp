"""FastMCP streamable-HTTP server for python-docsbox-mcp.

Tools delegate heavy work (linting, type-checking, formatting, package
metadata) to local processes; the MCP server itself is a thin orchestrator
with strict per-tool timeouts and bounded captured output.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse

from .corpus import Corpus, load_corpus
from .tools import (
    ast_dump as ast_dump_tool,
)
from .tools import (
    docs as docs_tool,
)
from .tools import (
    pep_lookup as pep_tool,
)
from .tools import (
    pip_info as pip_tool,
)
from .tools import (
    pyright as pyright_tool,
)
from .tools import (
    ruff as ruff_tool,
)
from .tools import (
    run_locally as run_locally_tool,
)
from .web import landing_page, llms_full_txt, llms_txt, robots_txt, sitemap_xml

logger = logging.getLogger("python-docsbox-mcp")


def _default_security(host: str, port: int) -> TransportSecuritySettings:
    """Build the DNS-rebinding-protection allow-list.

    Honours `PY_DOCSBOX_ALLOWED_HOSTS` and `PY_DOCSBOX_ALLOWED_ORIGINS` (both
    comma-separated). If `PY_DOCSBOX_DISABLE_DNS_PROTECTION=1` the protection
    is turned off entirely (only do this for tests).
    """
    if os.environ.get("PY_DOCSBOX_DISABLE_DNS_PROTECTION") == "1":
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        )

    extra_hosts = [
        h.strip() for h in os.environ.get("PY_DOCSBOX_ALLOWED_HOSTS", "").split(",") if h.strip()
    ]
    extra_origins = [
        o.strip() for o in os.environ.get("PY_DOCSBOX_ALLOWED_ORIGINS", "").split(",") if o.strip()
    ]
    base_hosts = [
        f"127.0.0.1:{port}",
        f"localhost:{port}",
        "127.0.0.1:*",
        "localhost:*",
        "python-mcp.afterrealism.com",
        "python-mcp.afterrealism.com:*",
    ]
    base_origins = [
        f"http://127.0.0.1:{port}",
        f"http://localhost:{port}",
        "https://python-mcp.afterrealism.com",
    ]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=list(dict.fromkeys(base_hosts + extra_hosts)),
        allowed_origins=list(dict.fromkeys(base_origins + extra_origins)),
    )


def _build_mcp(corpus: Corpus, http: httpx.AsyncClient, *, host: str, port: int) -> FastMCP:
    mcp = FastMCP(
        name="python-docsbox",
        instructions=(
            "Python developer tools: docs lookup, ruff lint/fix/format, "
            "pyright type-check, PEP lookup, pip metadata, AST dump, "
            "and a local-execution planner. All tools are read-only or "
            "operate on tempdirs; no host filesystem mutation outside of "
            "tempdirs."
        ),
        host=host,
        port=port,
        json_response=True,
        stateless_http=True,
        transport_security=_default_security(host, port),
    )

    docs_tool.register(mcp, corpus, http)
    ruff_tool.register(mcp)
    pyright_tool.register(mcp)
    pep_tool.register(mcp, http)
    pip_tool.register(mcp, http)
    ast_dump_tool.register(mcp)
    run_locally_tool.register(mcp)

    @mcp.custom_route("/", methods=["GET"])
    async def _index(_: Request) -> HTMLResponse:
        return HTMLResponse(landing_page())

    @mcp.custom_route("/health", methods=["GET"])
    async def _health(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok", "service": "python-docsbox-mcp"})

    @mcp.custom_route("/robots.txt", methods=["GET"])
    async def _robots(_: Request) -> PlainTextResponse:
        return PlainTextResponse(robots_txt(), media_type="text/plain; charset=utf-8")

    @mcp.custom_route("/sitemap.xml", methods=["GET"])
    async def _sitemap(_: Request) -> PlainTextResponse:
        return PlainTextResponse(sitemap_xml(), media_type="application/xml; charset=utf-8")

    @mcp.custom_route("/llms.txt", methods=["GET"])
    async def _llms(_: Request) -> PlainTextResponse:
        return PlainTextResponse(llms_txt(), media_type="text/markdown; charset=utf-8")

    @mcp.custom_route("/llms-full.txt", methods=["GET"])
    async def _llms_full(_: Request) -> PlainTextResponse:
        return PlainTextResponse(llms_full_txt(), media_type="text/markdown; charset=utf-8")

    return mcp


def _build_app(mcp: FastMCP) -> Any:
    """Build the underlying Starlette app (used by tests)."""
    return mcp.streamable_http_app()


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("PY_DOCSBOX_LOG", "info").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    bind = os.environ.get("PY_DOCSBOX_BIND", "127.0.0.1:7811")
    host, _, port_s = bind.partition(":")
    port = int(port_s or "7811")

    corpus = load_corpus(os.environ.get("PY_DOCSBOX_CORPUS_DIR"))
    http = httpx.AsyncClient(
        timeout=httpx.Timeout(15.0, connect=5.0),
        headers={"user-agent": "python-docsbox-mcp/0.1"},
    )

    mcp = _build_mcp(corpus, http, host=host, port=port)

    logger.info("python-docsbox-mcp listening on %s:%d (mcp at /mcp)", host, port)
    try:
        mcp.run(transport="streamable-http")
    finally:
        import asyncio

        try:
            asyncio.run(http.aclose())
        except (RuntimeError, OSError) as exc:
            logger.debug("ignoring httpx shutdown error: %s", exc)


if __name__ == "__main__":
    main()
