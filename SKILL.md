---
name: memcube
description: 结构化记忆管理 — 三层分层记忆（L1 痕迹/L2 模式/L3 世界观）的增删查演化，基于 MemOS MemCube 理念适配 OpenClaw 原生生态
---

# MemCube — 结构化记忆管理

吸取 MemOS（MemTensor）MemCube 分层记忆核心理念，基于 OpenClaw 原生工具链（lossless-claw + memory_search + MEMORY.md）实现轻量级结构化记忆管理。

## 核心理念

三个层次，逐级结晶：

```
L1 痕迹 (Traces)     →  memory/YYYY-MM-DD.md     → 原始对话日志、当天发生的事
L2 模式 (Patterns)   →  MEMORY.md                → 提炼后的规律、规则、偏好
L3 世界观 (Models)    →  skills/ + CORE_RULES.md  → 可执行的技能、核心法则
```

演化路径：L1 每日积累 → L2 跨天提取 → L3 固化技能

## 何时使用

必须使用本 skill 当任务涉及：
- **新增记忆** — 用户说"记住xxx"或发现值得持久化的信息
- **记忆查重** — 写 MEMORY.md 前，先查是否已有类似记录
- **记忆演化** — 从 L1 daily notes 提取模式升级到 L2 MEMORY.md
- **记忆检索** — 需要精确找历史决策/偏好/事实时
- **记忆维护** — 清理过时/冗余记录，标记置信度
- **记忆冲突** — 新信息与旧记忆矛盾时，按规则裁决

## 记忆记录格式

每条 MEMORY.md 中的记忆使用以下结构：

```markdown
### [标签] 记忆标题                                    <!-- @confidence @created @updated @source -->
- 核心事实或决策
- 关键细节（如有）
- 关联: [相关记忆标题] | 技能: skill-name
```

元数据字段：
| 字段 | 含义 | 可选值 |
|------|------|--------|
| `@confidence` | 确信度 | `verified`（已确认）/ `inferred`（推断）/ `speculative`（推测） |
| `@created` | 创建日期 | `YYYY-MM-DD` |
| `@updated` | 更新日期 | `YYYY-MM-DD` |
| `@source` | 信息来源 | `user`（用户口述）/ `observed`（观察推断）/ `derived`（从 L1 演化） |
| `@status` | 状态 | `active`（有效）/ `outdated`（过时）/ `archived`（归档） |
| `tags` | 标签 | 逗号分隔，如 `#网络 #配置` |

## 操作流程

### 新增记忆（add）

```
1. 用户说"记住xxx" 或 我观察到值得持久化的信息
2. 运行: python3 skills/memcube/scripts/memctl.py check "新记忆内容"
3. 如果有相似记忆 → 对比差异 → 决定合并/覆盖/追加
4. 写入 MEMORY.md，带完整元数据
5. 如果来源是 L1 daily notes → 在 daily note 中加 `[✓ 已演化]` 标记
```

### 记忆查重（check）

```
1. 运行: python3 skills/memcube/scripts/memctl.py check "待查内容"
2. 脚本返回: [相似记忆列表，含相似度分数]
3. 相似度 > 0.7 → 大概率重复，需手动判断合并还是补充
4. 相似度 0.4-0.7 → 可能相关但不重复，可加交叉引用
5. 相似度 < 0.4 → 新记忆，安全写入
```

### 记忆演化（evolve）

触发条件（每会话至少检查一次）：
- 当前有 L1 daily notes 存在
- 积累了 2+ 天的 daily notes 且 MEMORY.md 超过 24h 未更新

```
1. 读取最近 3-7 天的 memory/*.md
2. 提取重复出现的话题（用 memory_search 辅助）
3. 识别新规律/偏好/决策
4. 运行 check 确认不重复
5. 写入 MEMORY.md（带 @source: derived）
6. 在来源 daily notes 中标记 [✓ 已演化]
```

### 冲突裁决（resolve）

当新信息与旧记忆矛盾：
1. 以**更新时间更近**的一方为准
2. 如果来自用户直接口述（@source: user）→ 覆盖旧记录
3. 如果来自推断（@source: observed/derived）→ 标记旧记忆 @status: outdated，追加新记忆
4. 在旧记忆上加 `> ⚠️ 已过时，被 [新记忆标题] 覆盖 — YYYY-MM-DD`

### 记忆检索（search）

检索优先级（按需选择）：
```
需要精确关键词 → lcm_grep（全文/正则搜索）
需要语义理解   → memory_search（语义搜索）
需要深度展开   → lcm_expand_query（对话历史精确召回）
需要快速浏览   → memory_get（直接读文件）
```

## 记忆质量原则

1. **一个记忆一件事** — 不要一个大标题下塞 10 个不相关的点
2. **优先置信度标记** — 不确定的信息必须标 `@confidence: speculative`
3. **避免冗余** — 写入前必查重，相似内容合并而非重复
4. **保持鲜活** — 每 30 天检查一次，`@status: outdated` 的记忆及时清理
5. **可追溯** — 每条 L2 记忆应能回溯到 L1 来源

## 与现有系统配合

| 现有组件 | memcube 作用 |
|----------|------------|
| lossless-claw | 对话精确召回 → memcube 用 lcm_grep/lcm_expand_query 查历史细节 |
| memory_search | 语义搜索 → memcube 用 memory_search 做模糊匹配 |
| MEMORY.md | L2 长期记忆 → memcube 提供结构化读写 |
| memory/YYYY-MM-DD.md | L1 每日痕迹 → memcube 负责演化和标记 |
| save_self_evolution_skill | L3 技能结晶 → memcube 负责 L1→L2 升级，时机成熟再调用 |
| CORE_RULES.md | L3 核心法则 → memcube 不改动，只读 |

## 命令速查

```bash
# 查重
python3 skills/memcube/scripts/memctl.py check "记忆内容"

# 搜索
python3 skills/memcube/scripts/memctl.py search "关键词"

# 列出所有记忆（带元数据）
python3 skills/memcube/scripts/memctl.py list

# 演化检查（哪些 L1 需要升级到 L2）
python3 skills/memcube/scripts/memctl.py evolve-dry-run

# 统计
python3 skills/memcube/scripts/memctl.py stats
```
