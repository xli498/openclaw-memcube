---
name: auto-model-router
description: 自动模型路由 skill。根据任务复杂度自动选择模型：重任务用 DeepSeek V4 Pro，轻任务用 DeepSeek V4 Flash。全部走用户自有 API Key。
---

# Auto Model Router — 自动模型路由

## 路由规则

| 任务类型 | 模型 | 模式 |
|---------|------|------|
| **重任务**（多 step 工具编排、代码重构/生成、长文档分析、复杂推理、网络请求多轮） | `deepseek/deepseek-v4-pro` (DeepSeek-V4-Pro) | 主 agent 直接执行 |
| **轻任务**（单步查询、简单计算、知识问答、文本润色、状态检查、单次 web_fetch） | `deepseek/deepseek-v4-flash` (DeepSeek-V4-Flash) | spawn 子 agent 执行 |

## 判断流程

每接到任务，按以下顺序判断：

1. **检查 available_skills** — 有匹配 skill 直接使用
2. **评估复杂度**：
   - 需要工具链 ≥2 步 → **重任务** → 主 agent 用 DeepSeek-V4-Pro
   - 只需 1 步或纯知识回答 → **轻任务** → spawn 子 agent 用 DeepSeek-V4-Flash
3. **执行**

## 轻任务执行方式

```python
# Pseudocode: 用 sessions_spawn 在子 agent 中运行轻任务
sessions_spawn(
    task="<用户请求描述>",
    model="DeepSeek-V4-Flash",
    mode="run"
)
```

子 agent 天然拿到 minimal prompt（无完整 bootstrap），适合轻量任务。

## 重任务执行方式

直接在当前主会话用 DeepSeek V4 Pro 执行，用全部工具能力。

## 注意事项

- 不要在单次任务中切换模型——路由在**任务入口**做一次判断
- 子 agent 返回结果后直接呈现给用户，不二次加工
- 用户手动指定模型时忽略自动路由
