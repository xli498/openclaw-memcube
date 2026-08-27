# memctl.py 使用示例

以下输出均为对 `fixtures/demo-workspace` 实际运行的结果（`OPENCLAW_WORKSPACE` 指向该目录），可作为输出格式参考；具体数字以你的工作区为准。

## 环境准备

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
$ python3 scripts/memctl.py check "受控代理配置"

🔍 发现 1 条可能相关的记忆:

🔴 相似度: 100.00% | @verified | 2026-07-01 | [active]
   标题: 受控代理配置
   标签: 网络
   内容: - 代理变更前执行最小可逆验证，并记录验证证据。

⚠️  1 条高度相似（>70%），建议合并或跳过
```

## 2. 搜索（search）

精确搜索历史记忆。

```text
$ python3 scripts/memctl.py search "代理"

🔍 找到 1 条匹配 '代理' 的记忆:

  [L2] 受控代理配置 (匹配 2 次)
       @verified | 2026-07-01 | [active] | 标签: 网络
       - 代理变更前执行最小可逆验证，并记录验证证据。
```

## 3. 列表（list）

列出所有记忆及其元数据。

```text
$ python3 scripts/memctl.py list

🧠 MEMORY.md: 3 条记忆
   🟢 活跃: 2 | 🔴 过时: 1 | 📦 归档: 0

     确信度        创建日期         标题
-----------------------------------------------------------------
🟢   verified   2026-07-01   受控代理配置
🟢   inferred   2026-07-02   错误复盘规则
🔴   verified   2026-06-01   旧模型路由

⚠️  1 条过时记忆待清理
```

## 4. 演化检查（evolve-dry-run）

检查最近 7 天的 L1 daily notes 是否已演化到 MEMORY.md。

```text
$ python3 scripts/memctl.py evolve-dry-run

📋 最近 1 天的 daily notes:

  📝 2026-07-03.md: 4 行 [待演化]

📄 MEMORY.md 最后更新: 2026-08-27 11:12 (1.4 小时前)

⚠️  1 天的 daily notes 尚未演化
```

说明：`evolve-dry-run` 只报告 daily notes 的行数与演化状态（按内容中是否含 `[✓ 已演化]` 标记判断）；它不会给出“建议演化到哪个主题文件”的结论。话题归并由 `evolve` 的关键词统计辅助，最终由 agent 判断。

## 5. 统计（stats）

查看记忆系统整体状态。

```text
$ python3 scripts/memctl.py stats

🧠 MemCube 记忆统计
========================================
  总记忆条目:     3
  活跃:           2 🟢
  过时:           1 🔴
  归档:           0 📦
  旧格式(无元数据): 0 ⚡
  已确认:         2 ✅
  L2 条目 (##):   3
  L3 条目 (###):  0

📊 标签分布 (Top 10):
  #网络: 1
  #学习: 1
  #历史: 1

📄 MEMORY.md: 0.5 KB
📋 Daily Notes: 1 天, 0.1 KB
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
