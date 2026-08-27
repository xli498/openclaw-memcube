# MemCube 记忆格式规范

> 约定说明：`### [标签] 标题 <!-- @key value -->` 这套元数据格式是本仓库自定义的约定，用于 `memctl.py` 解析；它不是 OpenClaw 官方 `MEMORY.md` 的标准格式。宿主 agent 或其他工具不保证识别这些字段，迁移前请以目标系统文档为准。

## 条目结构

每个 L2/L3 记忆条目由四部分组成：

```
### [标签1,标签2] 记忆标题  <!-- @confidence verified @created 2026-05-28 @updated 2026-05-28 @source user @status active -->

记忆正文，支持多行 Markdown。
- 使用列表组织关键事实
- **加粗**重要细节

关联: [其他记忆标题]
技能: skill-name
```

## 字段说明

### 必填

| 字段 | 格式 | 说明 |
|------|------|------|
| 标题 | 纯文本 | 一句话概括记忆内容 |
| 置信度 | `@confidence verified|inferred|speculative` | verified=用户确认, inferred=从行为推断, speculative=推测 |
| 创建日期 | `@created YYYY-MM-DD` | 记忆首次记录的日期 |
| 来源 | `@source user|observed|derived` | user=用户口述, observed=观察, derived=从L1演化 |

### 可选

| 字段 | 格式 | 说明 |
|------|------|------|
| 标签 | `[tag1, tag2]` | 中括号内逗号分隔，用于分类搜索 |
| 更新日期 | `@updated YYYY-MM-DD` | 最后一次修改日期 |
| 状态 | `@status active|outdated|archived` | 缺省为 active |

## L2 与 L3 的区别

### L2 模式层 (## 二级标题)

- 描述"是什么"——观察到的规律、规则、偏好、事实
- 例子：用户偏好 DeepSeek API、下午效率最高、代理使用 Mihomo
- 存储在 MEMORY.md 中

### L3 世界观层 (# 一级标题或独立文件)

- 描述"怎么用"——可执行的技能、核心法则、系统配置
- 例子：CORE_RULES.md → 龙虾法则、skills/ 下的 SKILL.md
- L3 通常不对应单个记忆条目，而是独立文件或技能

## 演化规则

1. **L1 → L2**：某个话题在 2+ 天 daily notes 中出现 → 提炼为 L2 条目
2. **L2 → L3**：某条 L2 记忆持续应用 3+ 次且模式固化 → 考虑升级为 skill 或核心规则
3. **过时标记**：用户明确推翻旧信息时，旧条目标记 `@status outdated`，加覆盖注释

## 标签建议

| 标签 | 用途 |
|------|------|
| `#配置` | 系统配置相关 |
| `#网络` | 代理、连接相关 |
| `#模型` | LLM 模型、API 相关 |
| `#偏好` | 用户习惯、偏好 |
| `#技能` | 已安装/创建的 skills |
| `#教训` | 踩过的坑、经验 |
| `#任务` | 任务、项目相关 |
| `#定时` | cron 任务相关 |
