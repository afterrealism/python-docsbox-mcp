"""Bundled landing page + SEO / LLM static assets.

Each helper resolves first via `importlib.resources` (the package-resource
location used by an installed wheel) then falls back to the in-tree path so
that running directly out of a checkout still works.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

_FALLBACK_HTML = """<!doctype html>
<title>python-docsbox-mcp</title>
<h1>python-docsbox-mcp</h1>
<p>MCP endpoint at <code>/mcp</code>.</p>
"""

_FALLBACK_ROBOTS = "User-agent: *\nAllow: /\nDisallow: /mcp\n"

_FALLBACK_SITEMAP = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    "  <url><loc>https://python-mcp.afterrealism.com/</loc></url>\n"
    "</urlset>\n"
)

_FALLBACK_LLMS = "# python-docsbox-mcp\n\n> MCP server for Python developer tooling.\n"


def _read_resource(rel: str, fallback: str) -> str:
    """Read a packaged file under `python_docsbox_mcp/<rel>`.

    Prefer the installed-wheel path (importlib.resources). Fall back to the
    in-tree path for editable / dev installs. Last-resort fallback returns a
    minimal stub so the route still serves a valid response.
    """
    try:
        return resources.files("python_docsbox_mcp").joinpath(rel).read_text("utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass

    here = Path(__file__).resolve().parent / rel
    if here.exists():
        return here.read_text("utf-8")
    return fallback


def landing_page() -> str:
    return _read_resource("web/index.html", _FALLBACK_HTML)


def robots_txt() -> str:
    return _read_resource("web/robots.txt", _FALLBACK_ROBOTS)


def sitemap_xml() -> str:
    return _read_resource("web/sitemap.xml", _FALLBACK_SITEMAP)


def llms_txt() -> str:
    return _read_resource("web/llms.txt", _FALLBACK_LLMS)


def llms_full_txt() -> str:
    return _read_resource("web/llms-full.txt", _FALLBACK_LLMS)
