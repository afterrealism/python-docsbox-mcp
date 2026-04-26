"""Local-execution planner.

The MCP server itself is not allowed to execute arbitrary user code, that
would turn it into a remote shell. Instead this tool returns a structured
*plan* (a list of shell steps) that the calling agent can dispatch through
its own bash tool, on the user's machine. This pattern keeps the
responsibility for trust boundaries with the host agent.
"""

from __future__ import annotations

import base64
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="run_locally",
        description=(
            "Return a deterministic execution plan (list of shell steps) the "
            "calling agent can run on the user's host with its own bash tool. "
            "The plan creates a tempdir, writes the snippet, optionally "
            "installs deps via uv/pip, runs the script, and captures output. "
            "This server does NOT execute code itself."
        ),
    )
    async def run_locally(
        code: str = Field(description="Python source to execute on the user's host."),
        requirements: list[str] | None = Field(
            default=None,
            description="Optional pip-style requirement specifiers, e.g. ['httpx>=0.28'].",
        ),
        python: str = Field(
            default="python3",
            description="Python interpreter the agent should invoke.",
        ),
        runner: str = Field(
            default="auto",
            description="Dependency runner: 'auto', 'uv', 'pip', or 'none'.",
        ),
        timeout_s: int = Field(
            default=15,
            description="Suggested timeout the agent should pass to its bash tool.",
        ),
    ) -> dict[str, Any]:
        runner_norm = runner.lower()
        if runner_norm not in {"auto", "uv", "pip", "none"}:
            return {"ok": False, "error": "runner must be one of auto|uv|pip|none"}

        encoded = base64.b64encode(code.encode("utf-8")).decode("ascii")

        steps: list[dict[str, Any]] = []
        steps.append(
            {
                "name": "make_workdir",
                "shell": 'WORKDIR="$(mktemp -d -t pydocsbox-XXXXXX)" && echo "$WORKDIR"',
                "captures": "WORKDIR",
            }
        )
        steps.append(
            {
                "name": "write_script",
                "shell": (
                    f'{python} -c "import base64,sys,pathlib;'
                    'pathlib.Path(sys.argv[1]).write_bytes(base64.b64decode(sys.argv[2]))"'
                    f' "$WORKDIR/main.py" {encoded}'
                ),
            }
        )

        reqs = list(requirements or [])
        if reqs and runner_norm != "none":
            quoted = " ".join(_shell_quote(r) for r in reqs)
            if runner_norm in ("auto", "uv"):
                steps.append(
                    {
                        "name": "install_deps_uv",
                        "shell": (
                            "if command -v uv >/dev/null 2>&1; then "
                            f"uv pip install --system --quiet {quoted}; "
                            "else "
                            f"{python} -m pip install --quiet {quoted}; "
                            "fi"
                        ),
                    }
                )
            else:
                steps.append(
                    {
                        "name": "install_deps_pip",
                        "shell": f"{python} -m pip install --quiet {quoted}",
                    }
                )

        steps.append(
            {
                "name": "run_script",
                "shell": f'cd "$WORKDIR" && {python} main.py',
                "timeout_s": int(timeout_s),
            }
        )
        steps.append(
            {
                "name": "cleanup",
                "shell": 'rm -rf "$WORKDIR"',
                "best_effort": True,
            }
        )

        return {
            "ok": True,
            "plan": {
                "description": "Run a Python snippet locally with optional deps.",
                "interpreter": python,
                "runner": runner_norm,
                "requirements": reqs,
                "timeout_s": int(timeout_s),
                "steps": steps,
            },
            "note": (
                "Dispatch each step through your own bash tool, in order. "
                "Capture stdout/stderr per step. Treat any non-zero exit as a "
                "failure unless 'best_effort' is true."
            ),
        }


def _shell_quote(s: str) -> str:
    if not s:
        return "''"
    if all(c.isalnum() or c in "-_./=+,@:" for c in s):
        return s
    return "'" + s.replace("'", "'\\''") + "'"
