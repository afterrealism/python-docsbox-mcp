"""Shared helpers for tool implementations."""

from __future__ import annotations

import asyncio
import os
import shlex
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEOUT_S = 12.0
MAX_OUTPUT_BYTES = 200_000


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    duration_ms: int


@contextmanager
def scratch_file(name: str, contents: str) -> Iterator[Path]:
    """Yield a path to a temp file containing ``contents``.

    Cleaned up on context exit. The directory is also a tempdir so
    auxiliary files (e.g. pyrightconfig.json) can be written next to it.
    """
    with tempfile.TemporaryDirectory(prefix="pydocsbox-") as td:
        p = Path(td) / name
        p.write_text(contents, encoding="utf-8")
        yield p


async def run_command(
    argv: list[str],
    *,
    cwd: str | os.PathLike[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT_S,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
) -> CommandResult:
    """Run a subprocess with strict timeout and bounded captured output."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    full_env.setdefault("PYTHONIOENCODING", "utf-8")

    loop = asyncio.get_running_loop()
    started = loop.time()

    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            cwd=str(cwd) if cwd else None,
            stdin=asyncio.subprocess.PIPE if stdin is not None else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=full_env,
        )
    except FileNotFoundError as exc:
        return CommandResult(
            ok=False,
            exit_code=127,
            stdout="",
            stderr=f"command not found: {shlex.join(argv)} ({exc})",
            timed_out=False,
            duration_ms=0,
        )

    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(stdin.encode("utf-8") if stdin is not None else None),
            timeout=timeout,
        )
        timed_out = False
    except TimeoutError:
        proc.kill()
        try:
            stdout_b, stderr_b = await proc.communicate()
        except Exception:
            stdout_b, stderr_b = b"", b""
        timed_out = True

    duration_ms = int((loop.time() - started) * 1000)
    stdout = _trim(stdout_b)
    stderr = _trim(stderr_b)
    rc = proc.returncode if proc.returncode is not None else -1
    return CommandResult(
        ok=(rc == 0 and not timed_out),
        exit_code=rc,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        duration_ms=duration_ms,
    )


def _trim(buf: bytes) -> str:
    if len(buf) <= MAX_OUTPUT_BYTES:
        return buf.decode("utf-8", errors="replace")
    head = buf[: MAX_OUTPUT_BYTES // 2]
    tail = buf[-MAX_OUTPUT_BYTES // 2 :]
    return (
        head.decode("utf-8", errors="replace")
        + f"\n... [truncated {len(buf) - MAX_OUTPUT_BYTES} bytes] ...\n"
        + tail.decode("utf-8", errors="replace")
    )


def find_executable(name: str) -> str | None:
    """Locate an executable, honouring PATH."""
    from shutil import which

    return which(name)


def python_executable() -> str:
    """Return the interpreter that runs the server itself."""
    import sys

    return sys.executable
