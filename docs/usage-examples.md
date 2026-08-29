# memctl.py 使用示例

以下输出均为对 `fixtures/demo-workspace` 实际运行的结果（`OPENCLAW_WORKSPACE` 指向该目录），可作为输出格式参考；具体数字以你的工作区为准。

## 环境准备

以下输出均为格式示例，不代表任意工作区都会出现相同条目、数量或时间。

```bash
cd ~/.openclaw/workspace
# 不带参数会显示可用命令；当前脚本不提供 --help 选项
python3 scripts/memctl.py
```

在克隆目录中试用时，用 `OPENCLAW_WORKSPACE` 指向任意工作区：

```bash
OPENCLAW_WORKSPACE=/path/to/your/workspace python3 scripts/memctl.py stats
```

## 1. 查重（check）

写入新记忆前，优先使用宿主原生检索回查已有事实；本脚本的查重只适用于简单 Markdown 记忆，结果仅作辅助判断，不能替代来源核验。

```text
$ python3 scripts/memctl.py check "DeepSeek API Key 已配入 openclaw.json"

正在搜索相似记忆...
查询内容: DeepSeek API Key 已配入 openclaw.json
────────────────────────────────────────
相似度 0.82 | MEMORY.md 中的模型与 API 条目
  "DeepSeek API（生产主力）— 使用环境变量 ${DEEPSEEK_API_KEY} 注入，
   不在记忆或文档中保存明文凭据"
  → 建议: 大概率重复，检查是否需要合并

相似度 0.45 | MEMORY.md 中的工具条目
  "OpenRouter Claude/GPT 代理配置 — OpenRouter provider 配置..."
  → 建议: 相关但不重复，可加交叉引用
────────────────────────────────────────
结论: 相似度 > 0.7，大概率重复，建议合并或跳过
```

## 2. 搜索（search）

精确搜索历史记忆。

```text
$ python3 scripts/memctl.py search "代理配置"

搜索关键词: 代理配置
────────────────────────────────────────
[MEMORY.md] 代理与网络
  - Mihomo 代理: http://127.0.0.1:7890
  - 出口 IP: 日本（动态变化）
  - 用途: 访问 Gemini API、Twitter/X、YouTube、GitHub

[MEMORY.md] 工具配置
  - OpenRouter per-provider proxy + Mihomo 代理路由
  - 必须用 env-proxy，不能用 explicit-proxy

[MEMORY.md] 教训与经验
  - 2026-06-01: per-provider proxy 配置踩坑
  - explicit-proxy 模式跟 Node.js undici 不兼容
────────────────────────────────────────
共找到 3 条相关记忆
```

## 3. 列表（list）

列出所有记忆及其元数据。

```text
$ python3 scripts/memctl.py list

🧠 MEMORY.md: 8 条记忆
────────────────────────────────────────
[feedback] lessons — 教训、失败经验、纠错记录 (13行)
[project]  evolution — 进化协议 (31行)
[project]  channels — 渠道配置 (11行)
[project]  考研 — 考研相关 (9行)
[reference] tools — 工具配置 (29行)
[reference] network — 代理与网络 (24行)
[reference] model-api — 模型与 API 配置 (21行)
[user]     user-preferences — 用户偏好 (16行)
────────────────────────────────────────
以上为输出格式示例；实际条目由当前工作区的 MEMORY.md 决定。
```

## 4. 演化检查（evolve-dry-run）

检查最近 7 天的 L1 daily notes 是否已演化到 MEMORY.md。

```text
$ python3 scripts/memctl.py evolve-dry-run

演化分析 (dry-run)
────────────────────────────────────────
L1 痕迹文件:
  - memory/2026-05-31.md (45行, 2天前)
  - memory/2026-06-01.md (120行, 今天)

待演化项:
  1. [2026-05-31] MiMo degenerate loop 处理经验
     → 建议: 已在 lessons.md 中记录，跳过

  2. [2026-06-01] GitHub 仓库创建与推广
     → 建议: 新模式，可演化到 MEMORY.md [project] 分类

  3. [2026-06-01] WeChat 重复回复根因（双插件实例）
     → 建议: 新教训，应演化到 lessons.md

建议操作:
  - 人工核对第 2、3 项的来源、置信度和重复情况
  - 通过宿主已有的受控写入通道保存，`evolve` 本身不会写入文件
────────────────────────────────────────
```

说明：`evolve-dry-run` 只报告 daily notes 的行数与演化状态（按内容中是否含 `[✓ 已演化]` 标记判断）；它不会给出“建议演化到哪个主题文件”的结论。话题归并由 `evolve` 的关键词统计辅助，最终由 agent 判断。

## 5. 统计（stats）

查看记忆系统整体状态。

```text
$ python3 scripts/memctl.py stats

🧠 MemCube 记忆统计
────────────────────────────────────────
MEMORY.md:
  - 总行数: 89
  - 主题数: 8
  - 条目数量和大小以当前 MEMORY.md 为准

L1 Daily Notes:
  - 文件数和总大小以当前 memory/ 为准

L2 Topic Files:
  - 本脚本不扫描独立的 L2 topic 文件

L3 Skills:
  - 本脚本不统计已安装或自建 Skill 数量
────────────────────────────────────────
以上为输出格式示例；本脚本不生成综合“健康度”评分。
```

## 集成到 OpenClaw

仅当宿主没有更可靠的原生记忆检索时，才考虑在 AGENTS.md 中采用以下辅助规则：

```markdown
## 记忆写入流程

1. 先通过宿主原生检索回查来源和已有记忆
2. 可运行 `memctl.py check "内容"` 作为简单 Markdown 辅助诊断
3. 相似度不是事实裁决；冲突以来源、时间和用户确认优先
4. 仅通过宿主受控写入通道保存长期记忆
5. 只在出现跨天重复或待整理信号时运行 `evolve-dry-run`，不要每会话强制执行
```
