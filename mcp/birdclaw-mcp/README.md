# birdclaw MCP server

Use your local [birdclaw](https://birdclaw.sh) X/Twitter workspace from **Claude
Desktop** (or any MCP client) — read your timeline, mentions, bookmarks, and
likes, run full-text search, and generate birdclaw's native AI digest, all over
the Model Context Protocol.

This is the **Claude Desktop** counterpart to the `birdclaw` *skill* shipped in
this plugin. The skill runs in Claude Code; Claude Desktop loads MCP servers, not
skills — so to get birdclaw into Desktop you run this server.

> **Scope.** Your own account data only. birdclaw syncs your authenticated X
> transports; it **cannot** fetch arbitrary public tweets, other users'
> histories, or topic firehoses. Every value returned traces to a
> `birdclaw … --json` row — the server never invents data.

## Tools exposed

| Tool | What it does | Needs `OPENAI_API_KEY` |
|------|--------------|:---:|
| `birdclaw_pull(slice, limit, sync)` | Read a slice (`timeline`/`mentions`/`bookmarks`/`likes`); `sync=true` refreshes live first | no |
| `birdclaw_search(query, limit, bookmarked, hide_low_quality)` | FTS5 search over your cached tweets | no |
| `birdclaw_digest(period)` | Native AI digest (`today`/`24h`/`yesterday`/`week`) | yes |
| `birdclaw_inbox(limit, hide_low_signal)` | AI-ranked inbox of mentions/DMs | yes |

## Prerequisites

1. **birdclaw CLI on PATH** — `brew install steipete/tap/birdclaw`
2. **Initialized workspace** — `birdclaw init`, then import an archive to
   establish identity (`birdclaw import archive …`)
3. **Python 3.10+**
4. **`OPENAI_API_KEY`** — only for the digest / ranked-inbox tools; search and
   pull work without it.

## Install

Using [`uv`](https://docs.astral.sh/uv/) (recommended):

```bash
cd mcp/birdclaw-mcp
uv sync
uv run server.py    # smoke test: should start and wait on stdio (Ctrl-C to exit)
```

Or with plain pip:

```bash
cd mcp/birdclaw-mcp
pip install "mcp[cli]>=1.2.0"
python3 server.py
```

## Wire it into Claude Desktop

Edit your `claude_desktop_config.json`:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add a `birdclaw` entry under `mcpServers`. Use **absolute paths**.

With `uv` (recommended — handles the dependency for you):

```json
{
  "mcpServers": {
    "birdclaw": {
      "command": "uv",
      "args": ["run", "--directory", "/ABSOLUTE/PATH/TO/mcp/birdclaw-mcp", "server.py"],
      "env": { "OPENAI_API_KEY": "sk-..." }
    }
  }
}
```

With plain Python (requires `mcp` installed in that interpreter):

```json
{
  "mcpServers": {
    "birdclaw": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/mcp/birdclaw-mcp/server.py"],
      "env": { "OPENAI_API_KEY": "sk-..." }
    }
  }
}
```

Restart Claude Desktop. You should see the `birdclaw` tools appear. Try:
*"Pull my last 50 mentions and tell me which need a reply."*

> `OPENAI_API_KEY` in `env` is optional — omit it and the digest/inbox tools will
> return a clear error while search/pull keep working. birdclaw must already be
> able to reach your X transports for `sync=true` refreshes to succeed.
