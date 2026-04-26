# python-docsbox-mcp

A streamable-HTTP **Model Context Protocol** server that exposes Python developer
tools to LLM agents (Claude Code, OpenCode, Cursor, Continue, etc.).

Modeled on [`@sveltejs/mcp`](https://github.com/sveltejs/mcp): docs lookup, lint,
format, type-check, and a side-channel for local execution that delegates back
to the host agent's bash tool, never executes user code in-process.

## Tools

| name                | what it does                                                                              |
|---------------------|-------------------------------------------------------------------------------------------|
| `list_sections`     | list bundled doc sections, optionally filtered by package                                 |
| `get_documentation` | fetch a section by id (offline body if available, else live HTTP)                         |
| `ruff_check`        | lint a snippet (JSON diagnostics)                                                          |
| `ruff_fix`          | apply autofixes; return modified source + remaining diagnostics                           |
| `ruff_format`       | format with `ruff format` (stdin/stdout)                                                  |
| `pyright_check`     | type-check with pyright (structured diagnostics + summary)                                |
| `pep_lookup`        | fetch a PEP from peps.python.org (text or html)                                           |
| `pip_info`          | fetch package metadata from PyPI                                                          |
| `ast_dump`          | parse a snippet and return `ast.dump`; surfaces syntax errors with line/col               |
| `run_locally`       | return a deterministic shell-step plan the calling agent runs on the user's machine       |

## Endpoint

```
POST /mcp        streamable-HTTP JSON-RPC (MCP)
GET  /health     health probe
GET  /           landing page
```

Public production endpoint: `https://python-mcp.afterrealism.com/mcp`.

## Local development

```bash
uv venv
uv pip install -e '.[dev]'
python -m python_docsbox_mcp
# or
python-docsbox-mcp
```

Defaults: binds `127.0.0.1:7811`. Override with `PY_DOCSBOX_BIND=0.0.0.0:7811`.

Optional offline corpus directory: set `PY_DOCSBOX_CORPUS_DIR=/path/to/corpus`.
The server falls back to the bundled `corpus/manifest.toml` (URL-only entries)
otherwise.

## Connect from an agent

OpenCode / Claude Code (`~/.config/opencode/config.json` or
`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "python-docsbox": {
      "transport": {
        "type": "http",
        "url": "https://python-mcp.afterrealism.com/mcp"
      }
    }
  }
}
```

Cursor: add the same URL under "MCP servers" and restart.

See [`examples/opencode-config.json`](examples/opencode-config.json).

## Docker

```bash
docker build -t python-docsbox-mcp .
docker run --rm -p 7811:7811 python-docsbox-mcp
curl -s http://127.0.0.1:7811/health
```

## Trust model

- All linting/formatting/type-checking runs in tempdirs with bounded timeouts
  and bounded captured output. Tempdirs are cleaned up on exit.
- `run_locally` does **not** execute code on the server. It returns a plan;
  the calling agent dispatches the steps through its own host bash tool. This
  keeps the trust boundary at the agent/host, not at this MCP service.
- HTTP fetches (docs, PEPs, PyPI) follow redirects and have a 15 s timeout.

## License

MIT, see [`LICENSE`](LICENSE).
