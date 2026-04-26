"""Ruff lint, fix, and format tools."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .util import find_executable, run_command, scratch_file


def _ruff() -> str:
    exe = find_executable("ruff")
    if exe is None:
        raise RuntimeError("ruff binary not found on PATH")
    return exe


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="ruff_check",
        description=(
            "Lint a snippet of Python source with ruff. Returns the structured "
            "JSON diagnostic list (filename, code, message, location, fix)."
        ),
    )
    async def ruff_check(
        code: str = Field(description="Python source to lint."),
        select: str | None = Field(
            default=None,
            description="Optional comma-separated rule selectors (e.g. 'E,F,UP,SIM').",
        ),
        target_version: str | None = Field(
            default=None,
            description="Target Python version, e.g. 'py311'. Defaults to ruff's auto-detect.",
        ),
    ) -> dict[str, Any]:
        try:
            ruff = _ruff()
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}

        with scratch_file("snippet.py", code) as path:
            argv = [ruff, "check", "--output-format", "json"]
            if select:
                argv += ["--select", select]
            if target_version:
                argv += ["--target-version", target_version]
            argv.append(str(path))
            res = await run_command(argv, cwd=path.parent)
        diagnostics: list[Any]
        try:
            diagnostics = json.loads(res.stdout) if res.stdout.strip() else []
        except json.JSONDecodeError:
            diagnostics = []
        return {
            "ok": not res.timed_out,
            "exit_code": res.exit_code,
            "diagnostics": diagnostics,
            "stderr": res.stderr,
            "timed_out": res.timed_out,
            "duration_ms": res.duration_ms,
        }

    @mcp.tool(
        name="ruff_fix",
        description=(
            "Apply ruff autofixes to a Python snippet and return the modified "
            "source plus the diff and any remaining diagnostics."
        ),
    )
    async def ruff_fix(
        code: str = Field(description="Python source to fix."),
        select: str | None = Field(
            default=None,
            description="Optional rule selectors to apply (e.g. 'I,UP,SIM').",
        ),
        unsafe: bool = Field(
            default=False,
            description="Whether to apply unsafe fixes (--unsafe-fixes).",
        ),
    ) -> dict[str, Any]:
        try:
            ruff = _ruff()
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}

        with scratch_file("snippet.py", code) as path:
            argv = [ruff, "check", "--fix", "--exit-zero"]
            if unsafe:
                argv.append("--unsafe-fixes")
            if select:
                argv += ["--select", select]
            argv.append(str(path))
            fix_res = await run_command(argv, cwd=path.parent)
            fixed = path.read_text("utf-8")

            # Re-run check to surface remaining issues.
            recheck_argv = [ruff, "check", "--output-format", "json", str(path)]
            recheck = await run_command(recheck_argv, cwd=path.parent)

        try:
            remaining = json.loads(recheck.stdout) if recheck.stdout.strip() else []
        except json.JSONDecodeError:
            remaining = []

        return {
            "ok": not fix_res.timed_out,
            "code": fixed,
            "changed": fixed != code,
            "stderr": fix_res.stderr,
            "remaining_diagnostics": remaining,
            "timed_out": fix_res.timed_out or recheck.timed_out,
            "duration_ms": fix_res.duration_ms + recheck.duration_ms,
        }

    @mcp.tool(
        name="ruff_format",
        description=(
            "Format a Python snippet with `ruff format`. Returns the formatted source. Idempotent."
        ),
    )
    async def ruff_format(
        code: str = Field(description="Python source to format."),
        line_length: int | None = Field(
            default=None,
            description="Optional line length override.",
        ),
    ) -> dict[str, Any]:
        try:
            ruff = _ruff()
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}

        argv = [ruff, "format", "-"]
        if line_length is not None:
            argv += ["--line-length", str(int(line_length))]
        res = await run_command(argv, stdin=code)
        return {
            "ok": res.ok,
            "code": res.stdout if res.ok else code,
            "stderr": res.stderr,
            "exit_code": res.exit_code,
            "changed": res.ok and res.stdout != code,
            "timed_out": res.timed_out,
            "duration_ms": res.duration_ms,
        }
