# OpenClaw MemCube

> 你的 Agent 的记忆、模型路由、主动推送、会话拓扑——一个包，开箱即战。

---

## 里面有什么

```
openclaw-memcube/
├── SKILL.md                      <- 核心：结构化记忆管理
├── skills/
│   ├── auto-model-router/        <- 智能模型路由
│   ├── active-push/              <- 定时推送 & 监控
│   └── session-graph/            <- 实时会话拓扑
├── scripts/
│   └── memctl.py                 <- 零依赖的记忆控制台
└── references/
```

---

## 技能拆解

### auto-model-router -- 自动模型路由

每个任务自动匹配对的大脑。不问你"用哪个模型"。自己判断。

| 任务类型 | 模型 |
|---------|------|
| 重型（多步工具、代码生成、深度分析） | DeepSeek V4 Pro |
| 轻型（单步查询、问答、格式化） | DeepSeek V4 Flash |

原理：入口做复杂度判断。重型留住主 Agent。轻型 spawn 子 Agent。

### active-push -- 主动推送

没有守护进程？无所谓。三种方式：

1. cron + --announce 定时任务到点自动发你
2. sessions_send 后台脚本监测唤醒
3. cron + --light-context 轻量巡检

### session-graph -- 会话拓扑

session_list 的思维导图版。

---

## 安装

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/xli498/openclaw-memcube.git memcube
```

完了。零 npm 安装。零配置。

---

## 核心：三层记忆

L1 Traces -> memory/YYYY-MM-DD.md      每天发生了什么
L2 Patterns -> MEMORY.md              总结的规则和事实
L3 Models -> skills/ + CORE_RULES.md  可执行的技能和法则

scripts/memctl.py，纯 Python，零依赖。

灵感来自 MemOS (MemTensor)。不依赖向量数据库。就是一个 Python 文件。

---

## 架构

Agent 写的，给 Agent 用。每天在 WeChat、QQ Bot、小艺上跑的生产级技能。

## License

MIT。拿去。改进。分享。