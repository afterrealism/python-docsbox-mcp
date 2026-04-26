"""PEP lookup tool, fetches PEP metadata + body from peps.python.org."""

from __future__ import annotations

import re
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field

_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _strip_html(html: str, max_chars: int = 60_000) -> str:
    text = _TAG_RE.sub(" ", html)
    text = _WS_RE.sub(" ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars] + " ... [truncated]"
    return text


def register(mcp: FastMCP, http: httpx.AsyncClient) -> None:
    @mcp.tool(
        name="pep_lookup",
        description=(
            "Fetch a PEP by number from peps.python.org. Returns the title, "
            "canonical url, and a stripped plain-text body. Use this for "
            "questions about Python language proposals (PEPs)."
        ),
    )
    async def pep_lookup(
        pep: int = Field(description="PEP number, e.g. 8, 484, 695."),
        plain_text: bool = Field(
            default=True,
            description="If true, strip HTML and return plain text. If false, return raw HTML.",
        ),
    ) -> dict[str, Any]:
        if pep < 0 or pep > 9999:
            return {"ok": False, "error": "pep must be in [0, 9999]"}

        url = f"https://peps.python.org/pep-{pep:04d}/"
        try:
            resp = await http.get(url, follow_redirects=True)
            if resp.status_code == 404:
                return {"ok": False, "error": f"PEP {pep} not found", "url": url}
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            return {"ok": False, "error": f"fetch failed: {exc}", "url": url}

        html = resp.text
        title_m = _TITLE_RE.search(html)
        title = title_m.group(1).strip() if title_m else f"PEP {pep}"
        body = _strip_html(html) if plain_text else html
        return {
            "ok": True,
            "pep": pep,
            "url": url,
            "title": title,
            "body": body,
            "format": "text" if plain_text else "html",
        }
