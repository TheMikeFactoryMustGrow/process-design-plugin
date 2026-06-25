#!/usr/bin/env python3
"""Pull a slice of your own X/Twitter data via the birdclaw CLI and write it as JSONL.

This is a thin, defensive wrapper. It never invents data: every row comes from a
`birdclaw ... --json` invocation. Scope is your *own* account data only — timeline,
mentions, bookmarks, likes, or a full-text search over what birdclaw has cached.
Downstream skills (e.g. qa-agents) consume the JSONL this writes.

Usage:
    pull.py <slice> [--query Q] [--limit N] [--out PATH] [--sync] [--bookmarked]
                    [--hide-low-quality]

    <slice>  one of: timeline | mentions | bookmarks | likes | search
    --query  search terms (required for `search`)
    --limit  max rows (default 100)
    --out    JSONL output path (default: ./birdclaw-<slice>.jsonl)
    --sync   run `birdclaw sync <slice>` first to refresh live data before reading
    --bookmarked / --hide-low-quality  passthrough filters for `search`

Exit codes: 0 ok, 2 birdclaw missing, 3 birdclaw command failed, 4 bad args.
Machine-readable summary (count + path) is printed to stdout as one JSON line.
"""
import argparse
import json
import shutil
import subprocess
import sys

SLICES = ("timeline", "mentions", "bookmarks", "likes", "search")
# slices that birdclaw can refresh with `birdclaw sync <slice>`
SYNCABLE = ("timeline", "mentions", "bookmarks", "likes")


def die(code, msg):
    print(msg, file=sys.stderr)
    sys.exit(code)


def run_json(cmd):
    """Run a birdclaw command expecting a --json envelope on stdout."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        die(2, "birdclaw not found on PATH. Install: brew install steipete/tap/birdclaw")
    if proc.returncode != 0:
        die(3, f"`{' '.join(cmd)}` failed (exit {proc.returncode}):\n{proc.stderr.strip()}")
    out = proc.stdout.strip()
    if not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        die(3, f"`{' '.join(cmd)}` did not return JSON. stderr:\n{proc.stderr.strip()}")
    # birdclaw envelopes vary: a bare list, or {"data": [...]}, or {"tweets": [...]}.
    if isinstance(data, list):
        return data
    for key in ("data", "tweets", "results", "items"):
        if isinstance(data.get(key), list):
            return data[key]
    # single object -> wrap
    return [data]


def main():
    if shutil.which("birdclaw") is None:
        die(2, "birdclaw not found on PATH. Install: brew install steipete/tap/birdclaw")

    p = argparse.ArgumentParser()
    p.add_argument("slice", choices=SLICES)
    p.add_argument("--query", default=None)
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--out", default=None)
    p.add_argument("--sync", action="store_true")
    p.add_argument("--bookmarked", action="store_true")
    p.add_argument("--hide-low-quality", action="store_true")
    args = p.parse_args()

    if args.slice == "search" and not args.query:
        die(4, "`search` requires --query")

    out_path = args.out or f"./birdclaw-{args.slice}.jsonl"

    # Optional refresh of live data before reading.
    if args.sync and args.slice in SYNCABLE:
        sync_cmd = ["birdclaw", "sync", args.slice, "--limit", str(args.limit), "--json"]
        run_json(sync_cmd)  # we ignore the sync payload; we only care it succeeded

    # Build the read command.
    if args.slice == "search":
        read_cmd = ["birdclaw", "search", "tweets", args.query, "--limit", str(args.limit), "--json"]
        if args.bookmarked:
            read_cmd.append("--bookmarked")
        if args.hide_low_quality:
            read_cmd.append("--hide-low-quality")
    elif args.slice == "bookmarks":
        read_cmd = ["birdclaw", "search", "tweets", "--bookmarked", "--limit", str(args.limit), "--json"]
    else:
        # timeline / mentions / likes read back through search/sync envelopes
        read_cmd = ["birdclaw", "sync", args.slice, "--limit", str(args.limit), "--json"]

    rows = run_json(read_cmd)
    rows = rows[: args.limit]

    with open(out_path, "w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps({"slice": args.slice, "count": len(rows), "path": out_path}))


if __name__ == "__main__":
    main()
