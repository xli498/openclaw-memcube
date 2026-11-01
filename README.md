# OpenClaw MemCube

OpenClaw 记忆治理与轻量诊断参考——三层分层架构、来源/置信度/时效原则，以及一个零外部依赖的只读 Markdown 诊断脚本。它不替代已有记忆插件，也不应形成双写。

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
├── skills/                  # 独立的参考 Skill；不由 memctl 执行或安装
└── references/              # 参考资料
```

## 使用前先看

请先阅读[兼容性与记忆治理](./docs/compatibility-and-governance.md)。若运行时已有结构化记忆、对话召回或自动整理组件，默认不要直接安装或启用另一套长期记忆写入链路。

## 安装

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/xli498/openclaw-memcube.git memcube
```

仅想先在克隆目录中试用时，不需要安装 Skill：

```bash
git clone https://github.com/xli498/openclaw-memcube.git
cd openclaw-memcube
OPENCLAW_WORKSPACE=/path/to/your/workspace python3 scripts/memctl.py stats
```

安装到 `~/.openclaw/workspace/skills/memcube` 后，以下示例从
`~/.openclaw/workspace` 目录执行；克隆目录试用时，将命令中的
`skills/memcube/` 替换为当前目录下的 `scripts/`。

## 使用指南

### 指定工作区

`OPENCLAW_WORKSPACE` 用于指定要读取的 OpenClaw 工作区。工具会从该目录读取 `MEMORY.md` 和 `memory/YYYY-MM-DD.md`；未设置时默认使用 `~/.openclaw/workspace`。从克隆目录直接试用时，建议显式指定它：

```bash
OPENCLAW_WORKSPACE=/path/to/your/workspace python3 scripts/memctl.py search "关键词"
```

### memctl.py — 记忆控制台

memctl.py 是一个零依赖、**只读**的 Python 脚本，提供查重、搜索、列表和演化候选检查；它不新增、删除或改写记忆文件。

```bash
# 查重（写入前检查是否已有类似记忆）
python3 skills/memcube/scripts/memctl.py check "用户喜欢用 DeepSeek V4 Pro 模型"

# 输出会列出匹配条目的标题、标签、元数据摘要与相似度；相似度 > 0.7
# 仅表示“值得人工复核”，不是自动写入或合并操作。

# 搜索
python3 skills/memcube/scripts/memctl.py search "代理配置"

# 只搜索当前工作区的 MEMORY.md 结构化条目，不递归扫描其他文件。

# 列出所有记忆
python3 skills/memcube/scripts/memctl.py list

# 输出会区分 active、outdated、archived 和旧格式条目。

# 演化检查（哪些 L1 需要升级到 L2）
python3 skills/memcube/scripts/memctl.py evolve-dry-run

# 检查最近 7 天的 UTF-8 daily notes 是否标记为“已演化”；不会生成候选分数或修改文件。

# 统计
python3 skills/memcube/scripts/memctl.py stats

# 输出总条目、active/outdated/archived、已确认条目、L2/L3 数量和标签分布。
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

本仓库不会自行运行、安装或接入 WeChat、QQ Bot、小艺等渠道。它提供的是
只读 Markdown 诊断参考；任何生产接入都必须由使用者在自己的运行环境中审查、
配置并验证。

## License

MIT
