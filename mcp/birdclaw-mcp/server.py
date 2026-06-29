#!/usr/bin/env python3
"""birdclaw MCP server — read & analyze your OWN X/Twitter data from Claude Desktop.

This wraps the local [birdclaw](https://birdclaw.sh) CLI and exposes it over the
Model Context Protocol so MCP clients (Claude Desktop, etc.) can read and analyze
your own X world: timeline, mentions, bookmarks, likes, full-text search, the
native AI digest, and the ranked inbox.

SCOPE: your own account data only. birdclaw can sync your authenticated X
transports; it CANNOT fetch arbitrary public tweets, other users' histories, or
topic firehoses. Every value returned traces to a `birdclaw ... --json` row — the
server never invents data. If the CLI is missing or a command fails, the tool
returns a clear error string rather than fabricating a result.

Run:  python3 server.py        (stdio transport, the default for Claude Desktop)
"""
from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("birdclaw")

# Slices birdclaw can refresh with `birdclaw sync <slice>`.
SYNCABLE = ("timeline", "mentions", "bookmarks", "likes")
DIGEST_PERIODS = ("today", "24h", "yesterday", "week")


class BirdclawError(Exception):
    """Raised when the birdclaw CLI is missing or a command fails."""


def _run_json(cmd: list[str]) -> list[dict[str, Any]]:
    """Run a birdclaw command expecting a --json envelope on stdout.

    Normalizes birdclaw's varying envelopes (bare list, {"data":[...]},
    {"tweets":[...]}, etc.) to a list of row dicts. Raises BirdclawError on any
    failure so the caller can return a clean message instead of partial data.
    """
    if shutil.which("birdclaw") is None:
        raise BirdclawError(
            "birdclaw not found on PATH. Install: brew install steipete/tap/birdclaw"
        )
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise BirdclawError(
            "birdclaw not found on PATH. Install: brew install steipete/tap/birdclaw"
        )
    if proc.returncode != 0:
        raise BirdclawError(
            f"`{' '.join(cmd)}` failed (exit {proc.returncode}):\n{proc.stderr.strip()}"
        )
    out = proc.stdout.strip()
    if not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        raise BirdclawError(
            f"`{' '.join(cmd)}` did not return JSON. stderr:\n{proc.stderr.strip()}"
        )
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("data", "tweets", "results", "items"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    return [{"value": data}]


def _ok(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _err(exc: Exception) -> str:
    return json.dumps({"error": str(exc)}, ensure_ascii=False)


@mcp.tool()
def birdclaw_pull(slice: str, limit: int = 100, sync: bool = False) -> str:
    """Read a slice of YOUR OWN X data from the local birdclaw workspace.

    Args:
        slice: one of "timeline", "mentions", "bookmarks", "likes".
        limit: max rows to return (default 100).
        sync: if true, run `birdclaw sync <slice>` first to refresh live data.

    Returns a JSON object: {"slice", "count", "rows": [...]} or {"error": ...}.
    Scope is your own account only; this cannot reach arbitrary public tweets.
    """
    if slice not in SYNCABLE:
        return _err(ValueError(f"slice must be one of {SYNCABLE}, got {slice!r}"))
    try:
        if sync:
            _run_json(["birdclaw", "sync", slice, "--limit", str(limit), "--json"])
        rows = _run_json(["birdclaw", "sync", slice, "--limit", str(limit), "--json"])
        rows = rows[:limit]
        return _ok({"slice": slice, "count": len(rows), "rows": rows})
    except BirdclawError as exc:
        return _err(exc)


@mcp.tool()
def birdclaw_search(
    query: str,
    limit: int = 100,
    bookmarked: bool = False,
    hide_low_quality: bool = False,
) -> str:
    """Full-text search over YOUR OWN cached X data (FTS5).

    Args:
        query: search terms. Pass "" with bookmarked=true to list all bookmarks.
        limit: max rows (default 100).
        bookmarked: restrict to bookmarked tweets.
        hide_low_quality: drop low-quality matches.

    Returns {"query", "count", "rows": [...]} or {"error": ...}.
    """
    cmd = ["birdclaw", "search", "tweets"]
    if query:
        cmd.append(query)
    if bookmarked:
        cmd.append("--bookmarked")
    if hide_low_quality:
        cmd.append("--hide-low-quality")
    cmd += ["--limit", str(limit), "--json"]
    try:
        rows = _run_json(cmd)[:limit]
        return _ok({"query": query, "count": len(rows), "rows": rows})
    except BirdclawError as exc:
        return _err(exc)


@mcp.tool()
def birdclaw_digest(period: str = "today") -> str:
    """Generate birdclaw's native AI digest of YOUR OWN X activity.

    Requires OPENAI_API_KEY in the server environment.

    Args:
        period: one of "today", "24h", "yesterday", "week".

    Returns {"period", "digest": [...]} or {"error": ...}.
    """
    if period not in DIGEST_PERIODS:
        return _err(ValueError(f"period must be one of {DIGEST_PERIODS}, got {period!r}"))
    cmd = (
        ["birdclaw", "today", "--json"]
        if period == "today"
        else ["birdclaw", "digest", period, "--json"]
    )
    try:
        rows = _run_json(cmd)
        return _ok({"period": period, "digest": rows})
    except BirdclawError as exc:
        return _err(exc)


@mcp.tool()
def birdclaw_inbox(limit: int = 8, hide_low_signal: bool = True) -> str:
    """Return YOUR OWN AI-ranked X inbox (mentions/DMs scored for signal).

    Requires OPENAI_API_KEY in the server environment.

    Args:
        limit: max items (default 8).
        hide_low_signal: drop low-signal items (default true).

    Returns {"count", "rows": [...]} or {"error": ...}.
    """
    cmd = ["birdclaw", "inbox", "--score", "--limit", str(limit)]
    if hide_low_signal:
        cmd.append("--hide-low-signal")
    cmd.append("--json")
    try:
        rows = _run_json(cmd)[:limit]
        return _ok({"count": len(rows), "rows": rows})
    except BirdclawError as exc:
        return _err(exc)


if __name__ == "__main__":
    mcp.run()
