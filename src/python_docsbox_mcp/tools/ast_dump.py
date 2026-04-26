"""AST dump tool, surfaces parsed AST or syntax errors for a snippet."""

from __future__ import annotations

import ast
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="ast_dump",
        description=(
            "Parse a Python snippet and return its AST as a string. Useful for "
            "answering questions about how Python parses code, or for surfacing "
            "syntax errors with line/column locations."
        ),
    )
    async def ast_dump(
        code: str = Field(description="Python source to parse."),
        annotate_fields: bool = Field(
            default=True,
            description="Whether to include attribute names in the dump.",
        ),
        include_attributes: bool = Field(
            default=False,
            description="Whether to include line/column attributes.",
        ),
        indent: int = Field(
            default=2,
            description="Indentation level for the dump (>=0).",
        ),
    ) -> dict[str, Any]:
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return {
                "ok": False,
                "error": "syntax error",
                "message": exc.msg,
                "line": exc.lineno,
                "col": exc.offset,
                "text": exc.text,
            }

        try:
            dump = ast.dump(
                tree,
                annotate_fields=annotate_fields,
                include_attributes=include_attributes,
                indent=max(0, int(indent)),
            )
        except TypeError:
            # `indent` was added in 3.9, should always be available, but be safe.
            dump = ast.dump(
                tree,
                annotate_fields=annotate_fields,
                include_attributes=include_attributes,
            )
        if len(dump) > 200_000:
            dump = dump[:200_000] + "\n... [truncated]"
        return {
            "ok": True,
            "dump": dump,
            "node_count": sum(1 for _ in ast.walk(tree)),
        }
