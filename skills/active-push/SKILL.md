---
name: active-push
description: 主动推送能力。用 OpenClaw cron + sessions_send 实现后台守护效果。支持定时报告、异常告警、周期性检查结果推送到用户会话。
---

# Active Push — 主动推送

## 原理

OpenClaw 没有常驻 agent 进程（如 Hermes 的菜单栏 daemon），但可以通过以下机制实现类似效果：

1. **定时任务（cron）** — 周期触发检查逻辑
2. **`--announce` 模式** — cron 执行完后直接把结果推送到 channel
3. **`sessions_send`** — 运行时主动向主会话推送消息

## 推送模式

### 模式一：定时消息（cron + announce）
```bash
openclaw cron add \
  --name "每日总结" \
  --cron "0 22 * * *" \
  --message "做今天的总结" \
  --channel xiaoyi-channel \
  --announce
```

`--announce` 会在 cron 任务执行完后将最终回复 fallback 推送到 channel。

### 模式二：脚本后台循环 + sessions_send
```bash
# 后台运行脚本，需要时向主会话发消息
nohup bash -c '
  while true; do
    result=$(check_something)
    if [ "$result" != "ok" ]; then
      openclaw sessions send \
        --key "agent:main:direct:<session_id>" \
        --message "注意：$result"
    fi
    sleep 300
  done
' > /tmp/push_daemon.log 2>&1 &
```

### 模式三：cron + sub-agent（复杂检查）
```bash
openclaw cron add \
  --name "系统健康检查" \
  --every 30m \
  --message "运行一次系统健康检查，报告 CPU、内存、代理状态" \
  --model "DeepSeek-V4-Flash" \
  --channel xiaoyi-channel \
  --announce \
  --light-context
```

`--light-context` 让子 agent 用精简 prompt，适合轻量检查。

## 用法

用户说「每 X 分钟/小时/天提醒我 Y」或「定期检查 Z」时：
1. 用 cron add 创建定时任务
2. 复杂检查用 `--model DeepSeek-V4-Flash --light-context`
3. 简单脚本用 `--announce` 推结果
4. 告知用户任务已创建

## 注意事项

- cron 执行期间不能调用手机端工具（备忘录、日程、图库等）
- `--channel` 必须显式指定，不能用 last
- `--light-context` 用于轻量检查，减少 token 消耗
