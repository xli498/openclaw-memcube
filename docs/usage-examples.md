# memctl.py 使用示例

## 环境准备

```bash
cd ~/.openclaw/workspace
python3 scripts/memctl.py --help
```

## 1. 查重（check）

写入新记忆前，先查重避免重复。

```bash
$ python3 scripts/memctl.py check "DeepSeek API Key 已配入 openclaw.json"

正在搜索相似记忆...
查询内容: DeepSeek API Key 已配入 openclaw.json
────────────────────────────────────────
相似度 0.82 | memory/topics/model-api.md
  "DeepSeek API（生产主力）— 用户自己的 DeepSeek API Key: sk-5368…cc51，
   已配入 openclaw.json"
  → 建议: 大概率重复，检查是否需要合并

相似度 0.45 | memory/topics/tools.md
  "OpenRouter Claude/GPT 代理配置 — OpenRouter provider 配置..."
  → 建议: 相关但不重复，可加交叉引用
────────────────────────────────────────
结论: 相似度 > 0.7，大概率重复，建议合并或跳过
```

## 2. 搜索（search）

精确搜索历史记忆。

```bash
$ python3 scripts/memctl.py search "代理配置"

搜索关键词: 代理配置
────────────────────────────────────────
[memory/topics/network.md] 代理与网络
  - Mihomo 代理: http://127.0.0.1:7890
  - 出口 IP: 日本（动态变化）
  - 用途: 访问 Gemini API、Twitter/X、YouTube、GitHub

[memory/topics/tools.md] 工具配置
  - OpenRouter per-provider proxy + Mihomo 代理路由
  - 必须用 env-proxy，不能用 explicit-proxy

[memory/topics/lessons.md] 教训与经验
  - 2026-06-01: per-provider proxy 配置踩坑
  - explicit-proxy 模式跟 Node.js undici 不兼容
────────────────────────────────────────
共找到 3 条相关记忆
```

## 3. 列表（list）

列出所有记忆及其元数据。

```bash
$ python3 scripts/memctl.py list

MEMORY.md 记忆索引 (共 7 个主题)
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
总计: 164 行 / 8 个主题文件
```

## 4. 演化检查（evolve-dry-run）

检查哪些 L1 daily notes 需要升级到 L2 MEMORY.md。

```bash
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
  - 执行 evolve 将第 2、3 项写入 MEMORY.md
  - 第 1 项已存在，跳过
────────────────────────────────────────
```

## 5. 统计（stats）

查看记忆系统整体状态。

```bash
$ python3 scripts/memctl.py stats

记忆系统统计
────────────────────────────────────────
MEMORY.md:
  - 总行数: 89
  - 主题数: 8
  - 最大限制: 200 行
  - 使用率: 44.5%
  
L1 Daily Notes:
  - 文件数: 3
  - 总大小: 12.4 KB
  - 时间跨度: 2026-05-31 ~ 2026-06-01
  
L2 Topic Files:
  - 文件数: 8
  - 总大小: 8.2 KB
  - 最近更新: 2026-06-01
  
L3 Skills:
  - 已安装: 127
  - 自建: 5
────────────────────────────────────────
记忆健康度: 良好 ✅
  - 覆盖率: 7/8 核心领域已覆盖
  - 新鲜度: 最近 24h 内有更新
  - 冗余度: 0 条重复记录
```

## 集成到 OpenClaw

在 AGENTS.md 中添加自动查重规则：

```markdown
## 记忆写入流程

1. 写入前必须运行 `memctl.py check "内容"` 查重
2. 相似度 > 0.7 → 跳过或合并
3. 相似度 0.4-0.7 → 加交叉引用后写入
4. 相似度 < 0.7 → 安全写入
5. 每个会话结束时运行 `memctl.py evolve-dry-run` 检查演化
```
