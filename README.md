# MemCube — Structured Memory Management for OpenClaw

> Inspired by [MemOS (MemTensor)](https://github.com/MemTensor/MemOS) MemCube layered memory design, adapted as a lightweight, zero-dependency skill for OpenClaw.

## What It Does

MemCube brings structured memory management to your OpenClaw agent with a clear three-layer hierarchy:

```
L1 Traces    →  memory/YYYY-MM-DD.md       raw daily logs
L2 Patterns  →  MEMORY.md                  distilled rules, preferences, facts
L3 Models    →  skills/ + CORE_RULES.md    executable skills, core principles
```

## Features

- **Smart Dedup** — `check` before writing, never store the same thing twice
- **Structured Metadata** — every memory tagged with `@confidence` `@source` `@status` `@created`
- **Full-Text Search** — `search` with relevance scoring across all memories
- **Memory Evolution** — `evolve` detects cross-day patterns in daily notes for promotion to L2
- **Stats Dashboard** — `stats` gives you a bird's eye view of your memory health
- **Zero Dependencies** — pure Python 3, stdlib only
- **Backward Compatible** — reads existing MEMORY.md entries without metadata

## Commands

```bash
python3 memctl.py check "something to remember"    # dedup check before writing
python3 memctl.py search "keyword"                  # full-text search
python3 memctl.py list                              # list all memory entries
python3 memctl.py stats                             # memory health dashboard
python3 memctl.py evolve                            # find L1→L2 candidates
python3 memctl.py evolve-dry-run                    # check evolution status
```

## Install

```bash
# Clone into your OpenClaw workspace skills directory
cd ~/.openclaw/workspace/skills
git clone https://github.com/YOUR_USER/openclaw-memcube.git memcube
```

Or copy manually:

```bash
cp -r memcube/ ~/.openclaw/workspace/skills/memcube/
```

That's it. No `pip install`, no config, no setup.

## How It Compares to MemOS

| | MemOS | MemCube |
|---|---|---|
| **Memory Layers** | L1/L2/L3 + MemCube | L1/L2/L3 (same concept) |
| **Storage** | SQLite + Vector DB | Plain Markdown (MEMORY.md) |
| **Retrieval** | FTS5 + Vector Hybrid | FTS5 (via lossless-claw) + keyword |
| **Cloud** | Optional cloud service | 100% local |
| **Dependencies** | Multiple (plugin, DB, API) | Zero (Python stdlib) |
| **Multi-modal** | ✅ Images/charts | ❌ (out of scope) |
| **Tool Memory** | ✅ | ❌ (out of scope) |

MemCube doesn't try to replace MemOS. It borrows the layered memory philosophy and structured metadata concepts, then implements them in the simplest possible way that works with OpenClaw's existing ecosystem (lossless-claw, memory_search, MEMORY.md).

## License

MIT
