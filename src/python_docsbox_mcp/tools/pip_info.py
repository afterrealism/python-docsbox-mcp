"""PyPI metadata lookup."""

from __future__ import annotations

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field


def register(mcp: FastMCP, http: httpx.AsyncClient) -> None:
    @mcp.tool(
        name="pip_info",
        description=(
            "Fetch package metadata from PyPI (pypi.org/pypi/<name>/json). "
            "Returns latest version, summary, homepage, license, requires-python, "
            "and a sorted list of recent release versions."
        ),
    )
    async def pip_info(
        package: str = Field(description="PyPI distribution name, e.g. 'httpx'."),
        version: str | None = Field(
            default=None,
            description="Optional specific version to fetch. Defaults to latest.",
        ),
    ) -> dict[str, Any]:
        name = package.strip()
        if not name or any(c in name for c in (" ", "/", "\\")):
            return {"ok": False, "error": "invalid package name"}

        url = (
            f"https://pypi.org/pypi/{name}/{version}/json"
            if version
            else f"https://pypi.org/pypi/{name}/json"
        )
        try:
            resp = await http.get(url, follow_redirects=True)
            if resp.status_code == 404:
                return {"ok": False, "error": f"package not found: {name}", "url": url}
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        except httpx.HTTPError as exc:
            return {"ok": False, "error": f"fetch failed: {exc}", "url": url}
        except ValueError as exc:
            return {"ok": False, "error": f"invalid json: {exc}", "url": url}

        info = data.get("info", {})
        releases = data.get("releases", {})
        recent = sorted(releases.keys(), key=_version_sort_key, reverse=True)[:25]

        return {
            "ok": True,
            "name": info.get("name"),
            "version": info.get("version"),
            "summary": info.get("summary"),
            "home_page": info.get("home_page"),
            "project_urls": info.get("project_urls"),
            "license": info.get("license"),
            "requires_python": info.get("requires_python"),
            "requires_dist": info.get("requires_dist", []),
            "yanked": info.get("yanked", False),
            "recent_versions": recent,
            "url": url,
        }


def _version_sort_key(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in v.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)
