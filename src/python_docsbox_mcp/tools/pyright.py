"""Pyright type-check tool."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .util import find_executable, run_command, scratch_file

_DEFAULT_CONFIG = {
    "include": ["snippet.py"],
    "pythonVersion": "3.11",
    "typeCheckingMode": "standard",
    "reportMissingImports": "warning",
}


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="pyright_check",
        description=(
            "Type-check a Python snippet with pyright. Returns structured "
            "diagnostics: severity, range, rule, message."
        ),
    )
    async def pyright_check(
        code: str = Field(description="Python source to type-check."),
        python_version: str = Field(
            default="3.11",
            description="Python version pyright should target (e.g. '3.11').",
        ),
        strict: bool = Field(
            default=False,
            description="Enable strict typing mode.",
        ),
    ) -> dict[str, Any]:
        exe = find_executable("pyright")
        if exe is None:
            return {"ok": False, "error": "pyright binary not found on PATH"}

        with scratch_file("snippet.py", code) as path:
            cfg = dict(_DEFAULT_CONFIG)
            cfg["pythonVersion"] = python_version
            if strict:
                cfg["typeCheckingMode"] = "strict"
            (path.parent / "pyrightconfig.json").write_text(json.dumps(cfg), encoding="utf-8")
            res = await run_command(
                [exe, "--outputjson", str(path)],
                cwd=path.parent,
                timeout=20.0,
            )

        data: dict[str, Any]
        try:
            data = json.loads(res.stdout) if res.stdout.strip() else {}
        except json.JSONDecodeError:
            data = {"raw": res.stdout}

        diagnostics: list[dict[str, Any]] = []
        for raw in data.get("generalDiagnostics", []):
            d: dict[str, Any] = raw if isinstance(raw, dict) else {}
            diagnostics.append(
                {
                    "severity": d.get("severity"),
                    "rule": d.get("rule"),
                    "message": d.get("message"),
                    "range": d.get("range"),
                }
            )
        summary = data.get("summary", {})
        return {
            "ok": not res.timed_out,
            "exit_code": res.exit_code,
            "diagnostics": diagnostics,
            "summary": summary,
            "stderr": res.stderr,
            "timed_out": res.timed_out,
            "duration_ms": res.duration_ms,
        }
