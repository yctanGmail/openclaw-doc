#!/bin/bash
# 股票预警 cron 执行脚本
# 在交易时间每 15 分钟运行，触发预警时通过 OpenClaw 发送飞书消息

cd /home/yctan/.openclaw/workspace-lead

# 运行预警检查
output=$(python3 stock_price_alert.py 2>&1)

# 检查是否有预警触发
if echo "$output" | grep -q "触发预警："; then
    # 提取所有预警消息（从"共触发"开始的格式化的消息）
    alerts=$(echo "$output" | grep -A100 "共触发" | grep -v "^$" | tail -n +2)
    
    # 通过 OpenClaw 发送飞书消息
    if [ -n "$alerts" ]; then
        # 发送飞书消息
        openclaw message send --channel feishu --message "$alerts"
        
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 已发送预警消息"
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $output"
fi
