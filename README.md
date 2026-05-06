# .DS_Store

Per-file ambient notes for Claude Code, stored in `.DS_Store` under a custom record code (`llMD`).

The OS already maintains a B-tree keyed by filename in every directory you've ever opened in Finder. This plugin uses it as a sidecar-free, agent-managed documentation store.

## The idea

- **Notes auto-inject into context** when the agent reads a file.
- **The agent gets nudged** to refresh the note after edits that invalidate it.
- **Delete the file → the note orphans** → self-cleaning lifecycle. No stale docs.
- **No `.claude.md` sidecars.** No inline comment pollution. No `CLAUDE.md` per directory.

The trick: there is already a per-directory, per-filename, B-tree-indexed metadata store on every macOS machine. We're just reusing it for a payload it was not designed for.

## Install

```
/plugin marketplace add brysontang/.DS_Store
/plugin install dsstore-notes@dsstore
```

Or local dev:

```bash
git clone git@github.com:brysontang/.DS_Store.git ~/code/dsstore-notes
claude --plugin-dir ~/code/dsstore-notes
```

Requirements: macOS, [`uv`](https://github.com/astral-sh/uv) on PATH. Hook commands invoke `uv run` against the bundled `pyproject.toml`; the project auto-syncs on first invocation, no manual install step.

## How it works

### Read side — auto-inject

1. Agent calls `Read(file_path=…)`.
2. PreToolUse hook (`dsstore-inject`) fires.
3. Hook opens `<dir>/.DS_Store`, looks up the `llMD` record for that filename.
4. If found, hook emits `additionalContext` so the note appears in the agent's context for that turn — no separate read action needed.

### Write side — breadcrumb + nudge

1. Agent calls `Edit | Write | MultiEdit(file_path=…)`.
2. PostToolUse hook (`dsstore-breadcrumb`) fires:
   - Drops a breadcrumb at `$TMPDIR/claude_dsstore_breadcrumb` with the resolved path.
   - Emits `additionalContext`: the current note + a nudge to call `update_recent_note` if the edit invalidated it.
3. Agent calls `update_recent_note(note: str)`. The MCP tool reads the breadcrumb to know which file — **the agent never specifies the path**. That narrowness is the behavioral nudge: post-write, calling this tool is the cheapest available action. Good behavior becomes the path of least resistance.

## MCP tools

| Tool | Args | Purpose |
| --- | --- | --- |
| `update_recent_note` | `note: str` | Set the note on the file you most recently modified (path inferred from the breadcrumb). Empty string deletes. |
| `read_ambient_note` | `file_path: str` | Explicit lookup for any file. Escape hatch. |

## Layout

```
.DS_Store/                          # the repo (also the marketplace)
├── .claude-plugin/
│   ├── marketplace.json            # single-plugin marketplace catalog
│   └── plugin.json                 # Claude Code plugin manifest
├── .mcp.json                       # MCP server registration
├── hooks/hooks.json                # PreToolUse + PostToolUse bindings
├── dsstore_notes/                  # Python package (uv project)
│   ├── store.py                    # ds_store lib wrapper, llMD record I/O
│   ├── inject.py                   # PreToolUse hook (Read)
│   ├── breadcrumb.py               # PostToolUse hook (Edit/Write/MultiEdit)
│   └── server.py                   # FastMCP server
├── pyproject.toml
└── .DS_Store                       # this repo's own notes — eat your own dogfood
```

The committed `.DS_Store` files in this repo carry their own `llMD` notes for the source files. Load the plugin and read `dsstore_notes/store.py` — you'll see the note about `ds_store` lib quirks inject into context. The plugin demos itself.

## Caveats

- **macOS only.** `.DS_Store` is a Finder format. The `ds-store` Python lib runs on Linux, but `.DS_Store` files only naturally exist on macOS.
- **Finder also writes here.** Opening a directory in Finder rewrites `.DS_Store` with window state (`Iloc`, `bwsp`, `icvp`). Unknown record types like `llMD` are preserved, but if the repo's `.DS_Store` is committed, expect diff noise from any Finder click. Tradeoff for the demo.
- **Trust-the-agent design.** The agent owns cleanup. If your edits invalidate the note, you're expected to refresh it. If you can't trust the agent for that, the whole architecture collapses — but if you can't, agentic coding has bigger problems than stale notes.
- **`ds-store` is lightly maintained.** Works fine for the round-trips this plugin performs.
- **Codex support is partial.** The MCP tools work anywhere MCP is supported. The auto-inject-on-read hook is Claude-Code-specific (Codex doesn't fire hooks on file reads as of this writing).

## Why `llMD`

`.DS_Store` records are keyed by 4-byte codes. `llMD` = "LLM metadata" — generic for any agent framework, distinct from codes Finder uses (`Iloc`, `BKGD`, `bwsp`, `icvp`, etc.).

## Built because

> Do things because they're funny. The joke is the mnemonic.
