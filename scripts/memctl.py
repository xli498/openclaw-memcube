#!/usr/bin/env python3
"""
memctl.py — MemCube 记忆管理工具
MemOS MemCube 理念的 OpenClaw 轻量实现

命令:
  check "内容"      查重
  search "关键词"    全文搜索记忆
  list              列出所有记忆（带元数据摘要）
  evolve-dry-run    检查 L1→L2 演化候选
  evolve            分析 L1 中可演化的候选话题
  stats             统计概览

设计原则:
- 零外部依赖（纯 Python 标准库）
- 容错解析（新旧格式兼容）
- 不修改文件（add 由 agent 手动写入）
"""

import re
import sys
import os
from collections import Counter
from datetime import datetime

WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
MEMORY_MD = os.path.join(WORKSPACE, "MEMORY.md")
MEMORY_DIR = os.path.join(WORKSPACE, "memory")


def _daily_note_files():
    """返回 memory/ 下合法日期的 daily notes（YYYY-MM-DD.md），按日期倒序。

    仅匹配文件名形状不够：`9999-99-99.md` 也能通过正则，必须再用
    strptime 验证真实日历日期。
    """
    files = []
    try:
        names = os.listdir(MEMORY_DIR)
    except OSError:
        return []
    for f in names:
        if not re.match(r'^\d{4}-\d{2}-\d{2}\.md$', f):
            continue
        try:
            datetime.strptime(f[:-3], "%Y-%m-%d")
        except ValueError:
            continue
        files.append(f)
    return sorted(files, reverse=True)


def parse_memory_entries() -> list[dict]:
    """解析 MEMORY.md 中的所有记忆条目。
    兼容两种格式：
      ### [标签1,标签2] 标题  <!-- @key value @key2 value2 -->  (新)
      ## 标题  (旧，无元数据)
    """
    if not os.path.exists(MEMORY_MD):
        return []

    try:
        with open(MEMORY_MD, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print("⚠️ MEMORY.md 非 UTF-8 编码，无法解析（已跳过）", file=sys.stderr)
        return []
    except OSError as exc:
        print(f"⚠️ 无法读取 MEMORY.md: {exc}（已跳过）", file=sys.stderr)
        return []

    # 匹配 ## 或 ### 开头的标题行
    # group(1): heading level (## or ###)
    # group(3): optional [tags]
    # group(4): title text
    # group(5): optional metadata inside <!-- -->
    pattern = re.compile(
        r'^(#{2,3})\s+'                           # heading level
        r'(?:\[([^\]]*)\]\s*)?'                   # optional [tags]
        r'(.+?)'                                   # title (non-greedy)
        r'(?:\s*<!--\s*(.*?)\s*-->)?'             # optional <!-- @metadata -->
        r'\s*$',                                   # end of line
        re.MULTILINE
    )

    entries = []

    for match in pattern.finditer(content):
        heading_level = len(match.group(1))
        tags_str = match.group(2) or ""
        title = match.group(3).strip()
        metadata_str = match.group(4) or ""

        # 提取标签
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        # 解析元数据
        metadata = _parse_metadata(metadata_str)

        # 获取该条目后的内容
        body = _extract_body(content, match.end())

        entries.append({
            "heading_level": heading_level,
            "title": title,
            "tags": tags,
            "metadata": metadata,
            "body": body.strip(),
            "start_pos": match.start(),
            "end_pos": match.end() + len(body),
        })

    return entries


def _parse_metadata(meta_str: str) -> dict:
    """解析 @key value 格式的元数据"""
    matches = list(re.finditer(r"(?:^|\s)@([A-Za-z][\w-]*)(?:\s+|$)", meta_str))
    meta = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(meta_str)
        meta[match.group(1)] = meta_str[match.end():end].strip()
    return meta


def _extract_body(content: str, start: int) -> str:
    """提取标题后的正文，到下一个条目标题为止。

    任何 ## / ### 标题都会终止当前正文：## 条目必须被其后的 ### 子条目
    终止，否则 L3 子条目内容会被父条目正文吞并（注意 `#{1,2}` 匹配不了
    `###`，回溯后第三个 # 不是空白字符）。
    """
    rest = content[start:]
    stop_pattern = re.compile(r'\n#{1,3}\s')
    stop_match = stop_pattern.search(rest)
    if stop_match:
        return rest[:stop_match.start()]
    return rest


def _ngram_similarity(a: str, b: str, n: int = 2) -> float:
    """基于字符 n-gram 的 Jaccard 相似度"""
    def ngrams(s: str) -> set:
        s = s.lower()
        return {s[i:i + n] for i in range(len(s) - n + 1)}

    a_set = ngrams(a)
    b_set = ngrams(b)
    if not a_set or not b_set:
        return 0.0
    return len(a_set & b_set) / len(a_set | b_set)


def _keyword_match(query: str, text: str) -> float:
    """关键词匹配：查询中的词在文本中出现的比例"""
    # 提取查询中的关键片段（连续中文字符或英文单词）
    keywords = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', query.lower())
    if not keywords:
        return 0.0
    text_lower = text.lower()
    matched = sum(1 for kw in keywords if kw in text_lower)
    return matched / len(keywords)


def _simple_similarity(query: str, title: str, body: str) -> float:
    """综合相似度：标题匹配权重 0.6 + 关键词匹配权重 0.4"""
    if query.strip().casefold() == title.strip().casefold():
        return 1.0
    # 标题 n-gram 相似度（短文本，更精确）
    title_sim = _ngram_similarity(query, title, n=2)
    # 关键词在正文中的覆盖率
    kw_sim = _keyword_match(query, body)
    # 标题 + 正文前 200 字的综合匹配
    body_excerpt = body[:200]
    if body_excerpt:
        excerpt_sim = _ngram_similarity(query, body_excerpt, n=2)
    else:
        excerpt_sim = 0.0
    return title_sim * 0.5 + kw_sim * 0.25 + excerpt_sim * 0.25


# ─── 命令实现 ──────────────────────────────────────

def cmd_check(query: str):
    """查重：输入内容与已有记忆的相似度"""
    entries = parse_memory_entries()

    if not entries:
        print("📭 MEMORY.md 中暂无记忆条目")
        return

    results = []
    for entry in entries:
        score = _simple_similarity(query, entry['title'], entry['body'])
        if score > 0.08:
            results.append((score, entry))

    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        print("✅ 未发现相似记忆，可以安全写入")
        return

    print(f"🔍 发现 {len(results)} 条可能相关的记忆:\n")
    for score, entry in results:
        if score > 0.7:
            icon = "🔴"
        elif score >= 0.4:
            icon = "🟡"
        else:
            icon = "🟢"
        confidence = entry["metadata"].get("confidence", "?")
        created = entry["metadata"].get("created", "?")
        status = entry["metadata"].get("status", "active")

        print(f"{icon} 相似度: {score:.2%} | @{confidence} | {created} | [{status}]")
        print(f"   标题: {entry['title']}")
        print(f"   标签: {', '.join(entry['tags']) if entry['tags'] else '(无)'}")
        body_preview = entry['body'][:120].replace('\n', ' ')
        print(f"   内容: {body_preview}{'...' if len(entry['body']) > 120 else ''}")
        print()

    high = [r for r in results if r[0] > 0.7]
    mid = [r for r in results if 0.4 <= r[0] <= 0.7]
    if high:
        print(f"⚠️  {len(high)} 条高度相似（>70%），建议合并或跳过")
    elif mid:
        print(f"💡 {len(mid)} 条中度相关（40-70%），可考虑加交叉引用")
    else:
        print("✅ 所有匹配项相似度较低，可以安全写入")


def cmd_search(keyword: str):
    """全文搜索"""
    entries = parse_memory_entries()
    if not entries:
        print("📭 MEMORY.md 中暂无记忆条目")
        return

    keyword_lower = keyword.lower()
    results = []
    for entry in entries:
        text = f"{entry['title']} {entry['body']} {' '.join(entry['tags'])}"
        count = text.lower().count(keyword_lower)
        if count > 0:
            results.append((count, entry))

    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        print(f"🔍 未找到匹配 '{keyword}' 的记忆")
        return

    print(f"🔍 找到 {len(results)} 条匹配 '{keyword}' 的记忆:\n")
    for count, entry in results:
        confidence = entry["metadata"].get("confidence", "?")
        created = entry["metadata"].get("created", "?")
        status = entry["metadata"].get("status", "active")
        level = "L2" if entry["heading_level"] == 2 else "L3"

        print(f"  [{level}] {entry['title']} (匹配 {count} 次)")
        tag_str = ', '.join(entry['tags']) if entry['tags'] else '(无)'
        print(f"       @{confidence} | {created} | [{status}] | 标签: {tag_str}")
        body_preview = entry['body'][:150].replace('\n', ' ↵ ')
        print(f"       {body_preview}{'...' if len(entry['body']) > 150 else ''}")
        print()


def cmd_list():
    """列出所有记忆"""
    entries = parse_memory_entries()
    if not entries:
        print("📭 MEMORY.md 中暂无结构化记忆条目")
        print("   提示: 旧格式（无 <!-- @... --> 元数据）的 ## 条目也能识别")
        return

    active = [e for e in entries if e["metadata"].get("status", "active") == "active"]
    outdated = [e for e in entries if e["metadata"].get("status") == "outdated"]
    archived = [e for e in entries if e["metadata"].get("status") == "archived"]
    legacy = [e for e in entries if not e["metadata"]]

    print(f"🧠 MEMORY.md: {len(entries)} 条记忆")
    print(f"   🟢 活跃: {len(active)} | 🔴 过时: {len(outdated)} | 📦 归档: {len(archived)}")
    if legacy:
        print(f"   ⚡ 旧格式（无元数据）: {len(legacy)}")
    print(f"\n{'':4} {'确信度':10} {'创建日期':12} {'标题'}")
    print("-" * 65)

    for entry in entries:
        status = entry["metadata"].get("status", "active")
        confidence = entry["metadata"].get("confidence", "legacy" if not entry["metadata"] else "?")
        created = entry["metadata"].get("created", "?")
        status_icon = "🟢" if status == "active" else "🔴" if status == "outdated" else "⚡"
        print(f"{status_icon}   {confidence:10} {created:12} {entry['title'][:42]}")

    if outdated:
        print(f"\n⚠️  {len(outdated)} 条过时记忆待清理")


def cmd_evolve_dry_run():
    """检查 L1→L2 演化候选"""
    if not os.path.isdir(MEMORY_DIR):
        print("📭 memory/ 目录不存在")
        return

    files = _daily_note_files()

    if not files:
        print("📭 没有 daily notes")
        return

    recent = files[:7]
    print(f"📋 最近 {len(recent)} 天的 daily notes:\n")

    unevolved = 0
    for fname in recent:
        fpath = os.path.join(MEMORY_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            print(f"  ⚠️ {fname}: 非 UTF-8，已跳过")
            continue
        lines = content.strip().count('\n') + 1
        evolved = "[✓ 已演化]" in content
        icon = "✅" if evolved else "📝"
        status = "已演化" if evolved else "待演化"
        print(f"  {icon} {fname}: {lines} 行 [{status}]")
        if not evolved:
            unevolved += 1

    if os.path.exists(MEMORY_MD):
        mtime = datetime.fromtimestamp(os.path.getmtime(MEMORY_MD))
        hours = max(0, (datetime.now() - mtime).total_seconds() / 3600)
        print(f"\n📄 MEMORY.md 最后更新: {mtime.strftime('%Y-%m-%d %H:%M')} ({hours:.1f} 小时前)")
        if hours > 24:
            print("💡 超过 24 小时未更新，建议执行记忆演化")

    if unevolved > 0:
        print(f"\n⚠️  {unevolved} 天的 daily notes 尚未演化")
    else:
        print("\n✅ 所有 daily notes 已演化")


def cmd_evolve():
    """分析 L1 daily notes 中可演化的候选话题"""
    if not os.path.isdir(MEMORY_DIR):
        print("📭 memory/ 目录不存在")
        return

    files = _daily_note_files()[:7]

    all_keywords = Counter()
    file_contents = {}

    for fname in files:
        fpath = os.path.join(MEMORY_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            print(f"⚠️ 跳过非 UTF-8 daily note: {fname}")
            continue
        file_contents[fname] = content

        if "[✓ 已演化]" in content:
            continue

        # 提取中文关键短语
        phrases = re.findall(r'[\u4e00-\u9fff\w#@./-]{4,30}', content)
        for p in phrases:
            if re.match(r'^[\d\-.:/#@_]{4,}$', p):
                continue
            all_keywords[p.strip()] += 1

    repeated = [(p, c) for p, c in all_keywords.items() if c >= 2]
    repeated.sort(key=lambda x: x[1], reverse=True)

    if not repeated:
        print("✅ 未发现明显的重复话题需要演化")
        return

    print(f"🔍 发现 {len(repeated)} 个跨天重复出现的话题:\n")
    for phrase, count in repeated[:20]:
        containing = [f for f, c in file_contents.items() if phrase in c]
        print(f"  📌 '{phrase}' 出现 {count} 次 ({len(containing)} 天):")
        for cf in containing[:3]:
            print(f"     - {cf}")
        print()

    print(f"💡 建议: 将这些重复话题提炼为 L2 记忆写入 MEMORY.md")


def cmd_stats():
    """统计概览"""
    entries = parse_memory_entries()

    active = [e for e in entries if e["metadata"].get("status", "active") == "active"]
    outdated = [e for e in entries if e["metadata"].get("status") == "outdated"]
    archived = [e for e in entries if e["metadata"].get("status") == "archived"]
    legacy = [e for e in entries if not e["metadata"]]
    verified = [e for e in entries if e["metadata"].get("confidence") == "verified"]

    all_tags = []
    for e in entries:
        all_tags.extend(e["tags"])

    tag_counts = Counter(all_tags)
    l2 = sum(1 for e in entries if e["heading_level"] == 2)
    l3 = sum(1 for e in entries if e["heading_level"] == 3)

    print("🧠 MemCube 记忆统计")
    print("=" * 40)
    print(f"  总记忆条目:     {len(entries)}")
    print(f"  活跃:           {len(active)} 🟢")
    print(f"  过时:           {len(outdated)} 🔴")
    print(f"  归档:           {len(archived)} 📦")
    print(f"  旧格式(无元数据): {len(legacy)} ⚡")
    print(f"  已确认:         {len(verified)} ✅")
    print(f"  L2 条目 (##):   {l2}")
    print(f"  L3 条目 (###):  {l3}")

    if tag_counts:
        print(f"\n📊 标签分布 (Top 10):")
        for tag, count in tag_counts.most_common(10):
            print(f"  #{tag}: {count}")

    if os.path.exists(MEMORY_MD):
        size_kb = os.path.getsize(MEMORY_MD) / 1024
        print(f"\n📄 MEMORY.md: {size_kb:.1f} KB")

    if os.path.isdir(MEMORY_DIR):
        daily_files = _daily_note_files()
        total_kb = sum(os.path.getsize(os.path.join(MEMORY_DIR, f)) / 1024
                       for f in daily_files)
        print(f"📋 Daily Notes: {len(daily_files)} 天, {total_kb:.1f} KB")


# ─── main ─────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: memctl.py <命令> [参数]")
        print("命令: check | search | list | evolve-dry-run | evolve | stats")
        print("示例: python3 skills/memcube/scripts/memctl.py check '用户偏好 DeepSeek'")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "check": lambda: cmd_check(" ".join(args)),
        "search": lambda: cmd_search(" ".join(args)),
        "list": cmd_list,
        "evolve-dry-run": cmd_evolve_dry_run,
        "evolve": cmd_evolve,
        "stats": cmd_stats,
    }

    if cmd in commands:
        if cmd in ("check", "search"):
            # 空字符串参数（如 search ""）也会绕过 not args 校验，
            # 且 "".count 语义会让所有条目误报匹配，必须按内容判空
            if not " ".join(args).strip():
                print(f"❌ {cmd} 命令需要非空参数")
                sys.exit(1)
        commands[cmd]()
    else:
        print(f"❌ 未知命令: {cmd}")
        print("可用命令: check | search | list | evolve-dry-run | evolve | stats")
        sys.exit(1)


if __name__ == "__main__":
    main()
