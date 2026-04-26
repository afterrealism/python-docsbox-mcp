"""Sanity checks for the manifest corpus and the empty fallback."""

from __future__ import annotations

from pathlib import Path

from python_docsbox_mcp.corpus import _EmptyCorpus, _load_manifest_text, load_corpus


def test_manifest_loads_repo_fallback() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_text = (repo_root / "corpus" / "manifest.toml").read_text("utf-8")
    sections = _load_manifest_text(manifest_text)
    assert len(sections) >= 20
    ids = {s.id for s in sections}
    assert "stdlib/asyncio" in ids
    assert "mcp/python-sdk" in ids


def test_empty_corpus() -> None:
    c = _EmptyCorpus()
    assert c.list() == []
    assert c.get("stdlib/asyncio") is None


def test_load_corpus_returns_corpus(tmp_path: Path) -> None:
    # Empty dir → falls back to bundled / repo manifest.
    c = load_corpus(str(tmp_path))
    sections = c.list()
    # Either the bundled manifest is present (>=20) or empty fallback ([]).
    assert isinstance(sections, list)
