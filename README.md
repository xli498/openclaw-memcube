# OpenClaw MemCube

OpenClaw 的结构化记忆管理系统——三层分层架构，轻量级，零外部依赖。

## 为什么需要记忆系统

AI Agent 每次对话默认从空白状态开始。这意味着：
- 第 3 次对话时，它还在问你的名字
- 第 10 次对话时，它忘记了第 3 次学到的教训
- 100 次对话后，累积经验为零

MemCube 通过三层记忆架构解决这个问题，灵感来自 MemOS/MemTensor 的分层记忆理念。

## 三层记忆架构

```
L1 痕迹 (Traces)       memory/YYYY-MM-DD.md    原始对话日志
         ↓ 每日积累
L2 模式 (Patterns)     MEMORY.md               提炼后的规律/规则/偏好
         ↓ 跨天提取
L3 世界观 (Models)     skills/ + CORE_RULES.md  可执行的技能代码
```

## 文件结构

```
openclaw-memcube/
├── README.md                # 本文档
├── SKILL.md                 # 核心指令：OpenClaw 技能定义
├── scripts/
│   └── memctl.py            # 记忆控制台（零依赖 Python）
├── skills/
│   ├── auto-model-router/   # 自动路由：重型→主力模型，轻型→子Agent
│   ├── active-push/         # 主动推送：cron + sessions_send
│   └── session-graph/       # 会话拓扑可视化
└── references/              # 参考资料
```

## 安装

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/xli498/openclaw-memcube.git memcube
```

## 使用指南

### memctl.py — 记忆控制台

memctl.py 是一个零依赖的 Python 脚本，提供记忆的增删查演化功能。

```bash
# 查重（写入前检查是否已有类似记忆）
python3 skills/memcube/scripts/memctl.py check "用户喜欢用 DeepSeek V4 Pro 模型"

# 实际输出示例：
#  Searching memory for: "用户喜欢用 DeepSeek V4 Pro 模型"
#  Found 2 potential matches:
#    [0.82] [模型偏好] 主力模型为 deepseek/deepseek-v4-pro (MEMORY.md:45)
#    [0.56] [配置] DeepSeek API 配置 (MEMORY.md:120)
#  ⚠️ 第1条相似度>0.7，建议合并而非新增。

# 搜索
python3 skills/memcube/scripts/memctl.py search "代理配置"

# 实际输出示例：
#  Searching for: "代理配置"
#  Found 3 results:
#    [1] [网络] Mihomo 代理端口 7890, envProxy 模式 ▸ MEMORY.md:78
#    [2] [踩坑] explicit-proxy 与 undici 不兼容 ▸ .learnings/ERRORS.md:12
#    [3] [TTS] edge-tts 代理配置 port 5050 ▸ memory/2025-05-31.md

# 列出所有记忆
python3 skills/memcube/scripts/memctl.py list

# 实际输出示例：
#  ══════════════════════════════════════════════
#    Memory Index — 23 entries
#  ══════════════════════════════════════════════
#    [ACTIVE    ] 模型偏好: deepseek-v4-pro       @verified 2025-05-20
#    [ACTIVE    ] Mihomo 代理配置                  @verified 2025-05-22
#    [ACTIVE    ] 微信+QQ 双渠道                   @verified 2025-05-25
#    [OUTDATED  ] OpenRouter 配置 (已迁移到 DeepSeek) @2025-05-15
#    [SPECULATIVE] MiMo 模型表现评估               @speculative 2025-06-01
#  ══════════════════════════════════════════════

# 演化检查（哪些 L1 需要升级到 L2）
python3 skills/memcube/scripts/memctl.py evolve-dry-run

# 实际输出示例：
#  Scanning daily notes for patterns...
#    memory/2025-05-31.md: 3 potential patterns
#    memory/2025-05-30.md: 1 potential pattern
#    memory/2025-05-29.md: skipped (already evolved)
#  ─────────────────────────────────────
#  Candidates for L1→L2 evolution:
#    [0.91] "HTTP Header 中文字符导致 ByteString 错误" (appeared 3 times)
#    [0.85] "插件去重需要完整重启进程" (appeared 2 times)
#    [0.72] "MiMo reasoning=True 循环问题" (appeared 4 times)

# 统计
python3 skills/memcube/scripts/memctl.py stats

# 实际输出示例：
#  Memory Statistics
#  ─────────────────
#  Total memories:    23
#  Active:            18
#  Outdated:           3
#  Archived:           2
#  By confidence:
#    Verified:        15
#    Inferred:         5
#    Speculative:      3
#  By source:
#    User:            12
#    Observed:         7
#    Derived:          4
#  L1 daily notes:    14 files (2025-05-20 ~ 2025-06-02)
```

## 记忆记录格式

每条 MEMORY.md 中的记忆使用以下结构：

```markdown
### [标签] 记忆标题  <!-- @confidence @created @updated @source -->
- 核心事实或决策
- 关键细节
- 关联: [相关记忆] | 技能: skill-name
```

元数据：
| 字段 | 含义 | 可选值 |
|------|------|--------|
| `@confidence` | 确信度 | `verified` / `inferred` / `speculative` |
| `@created` | 创建日期 | `YYYY-MM-DD` |
| `@updated` | 更新日期 | `YYYY-MM-DD` |
| `@source` | 信息来源 | `user` / `observed` / `derived` |

## 操作原则

1. **写入前必查重** — 相似度 > 0.7 则合并而非新增
2. **一个记忆一件事** — 避免大块混杂
3. **优先置信度标记** — 不确定的信息标注为 speculative
4. **冲突时以新为准** — 新信息覆盖旧记忆，旧记忆标记为 outdated
5. **可追溯** — L2 记忆应能回溯到 L1 来源

## 配套技能

- **auto-model-router** — 自动判断任务复杂度，路由到合适模型
- **active-push** — 三种推送方案：cron 定时、sessions_send 监测、轻量巡检
- **session-graph** — 会话拓扑思维导图（非列表）

## 生产状态

每天在 WeChat、QQ Bot、小艺渠道上运行。

## License

MIT
