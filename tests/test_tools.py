"""Tool smoke tests that don't require network or external binaries."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_ast_dump_ok() -> None:
    from python_docsbox_mcp.tools.ast_dump import register

    captured: dict[str, object] = {}

    class FakeMCP:
        def tool(self, **_kwargs):
            def deco(fn):
                captured[_kwargs["name"]] = fn
                return fn

            return deco

    register(FakeMCP())  # type: ignore[arg-type]
    result = await captured["ast_dump"](code="x = 1\n")  # type: ignore[operator]
    assert result["ok"] is True
    assert "Assign" in result["dump"]
    assert result["node_count"] >= 3


@pytest.mark.asyncio
async def test_ast_dump_syntax_error() -> None:
    from python_docsbox_mcp.tools.ast_dump import register

    captured: dict[str, object] = {}

    class FakeMCP:
        def tool(self, **_kwargs):
            def deco(fn):
                captured[_kwargs["name"]] = fn
                return fn

            return deco

    register(FakeMCP())  # type: ignore[arg-type]
    result = await captured["ast_dump"](code="def (:")  # type: ignore[operator]
    assert result["ok"] is False
    assert result["error"] == "syntax error"
    assert result["line"] is not None


@pytest.mark.asyncio
async def test_run_locally_plan_shape() -> None:
    from python_docsbox_mcp.tools.run_locally import register

    captured: dict[str, object] = {}

    class FakeMCP:
        def tool(self, **_kwargs):
            def deco(fn):
                captured[_kwargs["name"]] = fn
                return fn

            return deco

    register(FakeMCP())  # type: ignore[arg-type]
    result = await captured["run_locally"](  # type: ignore[operator]
        code="print('hi')",
        requirements=["httpx>=0.28"],
        python="python3",
        runner="auto",
        timeout_s=10,
    )
    assert result["ok"] is True
    plan = result["plan"]
    step_names = [s["name"] for s in plan["steps"]]
    assert step_names[0] == "make_workdir"
    assert "run_script" in step_names
    assert plan["requirements"] == ["httpx>=0.28"]
