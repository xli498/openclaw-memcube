#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="$ROOT/fixtures/demo-workspace"
run() { OPENCLAW_WORKSPACE="$WS" python3 "$ROOT/scripts/memctl.py" "$@"; }
run search "代理" | grep -q "受控代理配置"
run check "受控代理配置" | grep -q "相似度"
run list | grep -q "受控代理配置"
run stats | grep -q "总记忆条目"
run evolve-dry-run | grep -q "daily notes"
run evolve | grep -Eq "重复出现|未发现"

# Formal L3 entries must be listed independently rather than being consumed
# by the preceding L2 body.
TMP_WS="$(mktemp -d)"
trap 'rm -rf "$TMP_WS"' EXIT
mkdir -p "$TMP_WS/memory"
cat > "$TMP_WS/MEMORY.md" <<'EOF'
## Parent
Parent body
### [tag] Child One
Child body one
### [tag] Child Two
Child body two
EOF
OPENCLAW_WORKSPACE="$TMP_WS" python3 "$ROOT/scripts/memctl.py" list | grep -q "Child One"
OPENCLAW_WORKSPACE="$TMP_WS" python3 "$ROOT/scripts/memctl.py" list | grep -q "Child Two"
OPENCLAW_WORKSPACE="$TMP_WS" python3 "$ROOT/scripts/memctl.py" stats | grep -q "总记忆条目:     3"
# Exact titles must reach the documented duplicate threshold; archived entries
# must not inflate active counts, and metadata values may contain @ characters.
cat > "$TMP_WS/MEMORY.md" <<'EOF'
### [tag] Exact title <!-- @status archived @source user@example.com -->
Archived body
EOF
OPENCLAW_WORKSPACE="$TMP_WS" python3 "$ROOT/scripts/memctl.py" check "Exact title" | grep -q "高度相似（>70%）"
OPENCLAW_WORKSPACE="$TMP_WS" python3 "$ROOT/scripts/memctl.py" list | grep -q "活跃: 0"
OPENCLAW_WORKSPACE="$TMP_WS" python3 "$ROOT/scripts/memctl.py" list | grep -q "归档: 1"
echo "memctl fixture tests passed"
