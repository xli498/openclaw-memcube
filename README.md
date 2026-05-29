# OpenClaw MemCube

**Agent 的记忆系统。三分钟装好，生产级，零外部依赖。**

---

## 为什么存在

Agent 没有记忆就是傻子。每次对话都像第一次见面。

市场上现有的"记忆方案"？
- 向量数据库。太重。
- 云端服务。隐私风险。
- 一套微服务架构。就为了记住一句话？认真的？

所以我们自己造了一个。

---

## 怎么工作

```
openclaw-memcube/
├── SKILL.md                ← 核心指令：怎么用
├── skills/
│   ├── auto-model-router/  ← 自动判断：重型任务上 DeepSeek V4 Pro，轻量任务上 V4 Flash
│   ├── active-push/        ← 没有守护进程？cron + sessions_send 搞定
│   └── session-graph/      ← session_list 的思维导图版
├── scripts/
│   └── memctl.py           ← 零依赖的记忆控制台。纯 Python。
└── references/
```

**核心设计——三层记忆架构（灵感来自 MemOS/MemTensor）：**

| 层级 | 位置 | 存什么 |
|------|------|--------|
| L1 Traces | memory/YYYY-MM-DD.md | 每天发生了什么 |
| L2 Patterns | MEMORY.md | 学到的规则和事实 |
| L3 Models | skills/ + CORE_RULES.md | 可执行的技能代码 |

memctl.py — 一个 Python 文件。查重。搜索。演化分析。统计。全部零依赖。

这就是第一性原理。不要数据库，不要微服务，不要 Kubernetes。**就一个文件。**

---

## 配套技能

**auto-model-router：** 入口判断任务复杂度。重型任务→主力模型。轻型→spawn 子 Agent。不需要问"用哪个模型"。

**active-push：** 三种推送方案。cron 定时。sessions_send 监测。--light-context 巡检。

**session-graph：** 会话拓扑可视化。不是列表。是思维导图。

---

## 安装

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/xli498/openclaw-memcube.git memcube
```

完了。不用 npm install。不用 docker compose。不用改一行配置。

---

## 生产状态

每天在 WeChat、QQ Bot、小艺上跑。不是玩具。是每天用的。

## License

MIT。复制。改进。分享。
