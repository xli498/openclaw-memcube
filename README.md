# 🦞 OpenClaw MemCube + Skills Toolkit

> _Your agent's memory, model switching, push notifications, and session topology — packaged for war._

---

## What's Inside

```
openclaw-memcube/
├── SKILL.md                      ← Root: MemCube structured memory management
├── skills/
│   ├── auto-model-router/        ← 🧠 Intelligence-driven model switching
│   ├── active-push/              ← 📡 Cron-based background push & monitoring
│   └── session-graph/            ← 🕸️ Real-time session topology visualization
├── scripts/
│   └── memctl.py                 ← Zero-dep memory control panel
└── references/
```

---

## ⚡ Skills Breakdown

### 🧠 auto-model-router — 自动模型路由

Routes every task to the right brain without asking.

| Task Type | Model | Credentials |
|-----------|-------|-------------|
| 🔴 Heavy (multi-step tools, code gen, deep analysis) | **DeepSeek V4 Pro** | Your API Key |
| 🟢 Light (single query, Q&A, formatting) | **DeepSeek V4 Flash** | Your API Key |

**How:** Complexity check at task entry. Heavy stays on main agent. Light spawns a sub-agent with minimal prompt — faster, cheaper, zero context bloat.

### 📡 active-push — 主动推送

No daemon? No problem. Three ways to push without a constant process:

1. **`cron + --announce`** — Scheduled task auto-delivers results to your chat
2. **`sessions_send`** — Background script wakes up and pushes when something happens
3. **`cron + --light-context`** — Minimal prompt sub-agent runs periodic checks on a budget

**Use case:** "Check my server every 10 minutes and yell at me if it's down."

### 🕸️ session-graph — 会话拓扑

Turns `sessions_list` into a live network map.

```
━━ Session Topology ━━━━━━━━━━━━━━━━━━━━
┃ 🧵 xiaoyi-channel (active)
┃  ├─ 💬 weixin
┃  ├─ 💬 qqbot
┃  ├─ ⏰ douyin-spark 07:30
┃  ├─ ⏰ weather-daily 08:00   ✅
┃  └─ ⏰ football-results 08:00 ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Ask:** "Show me my session topology" or "What's running in the background?"

---

## 📦 Install

Clone into your OpenClaw workspace skills directory:

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/xli498/openclaw-memcube.git memcube
```

That's it. Skills auto-detect. Zero npm install, zero config.

---

## 🧠 Original: MemCube Memory System

Three-layer structured memory for OpenClaw:

```
L1 Traces    →  memory/YYYY-MM-DD.md       raw daily logs
L2 Patterns  →  MEMORY.md                  distilled rules & facts
L3 Models    →  skills/ + CORE_RULES.md    executable skills & principles
```

Commands via `scripts/memctl.py`:

```bash
python3 memctl.py search "keyword"     # full-text search
python3 memctl.py check "fact"         # dedup before writing
python3 memctl.py stats                # memory health dashboard
python3 memctl.py evolve               # promote daily logs → L2 patterns
```

> Inspired by [MemOS (MemTensor)](https://github.com/MemTensor/MemOS) — zero dependencies, pure Python.

---

## 🏗️ Architecture

Built for agents, by agents. These aren't toy plugins — they're production skills running daily on a live OpenClaw instance across WeChat, QQ Bot, and Xiaoyi channels.

---

## License

MIT — steal, fork, improve, share.
