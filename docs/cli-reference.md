# memctl CLI Reference

`memctl.py` is a local Markdown diagnostic tool. It reads `MEMORY.md` and `memory/YYYY-MM-DD.md` from `OPENCLAW_WORKSPACE` (default: `~/.openclaw/workspace`).

```bash
OPENCLAW_WORKSPACE=/path/to/workspace python3 scripts/memctl.py search "关键词"
```

| Command | Input | Effect |
|---|---|---|
| `check <text>` | candidate memory | similarity review; read-only |
| `search <keyword>` | keyword | search parsed entries; read-only |
| `list` / `stats` | none | inventory and statistics; read-only |
| `evolve-dry-run` / `evolve` | none | prints candidates from daily notes; does not write files |

Exit code `1` means invalid or missing command input; command-specific successful inspection returns `0`. Fixture tests deliberately set `OPENCLAW_WORKSPACE`; never point automated tests at a real user workspace.
