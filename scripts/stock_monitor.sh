#!/bin/bash
# 股票价格预警监控入口脚本
# 由 cron 调用，检查价格并发送预警

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 运行价格检查
python3 stock_price_alert.py

# 检查是否有待发送的预警
if [ -f "pending_alerts.json" ]; then
    ALERT_COUNT=$(python3 -c "import json; print(len(json.load(open('pending_alerts.json'))))" 2>/dev/null || echo "0")
    if [ "$ALERT_COUNT" -gt "0" ]; then
        echo "有 $ALERT_COUNT 条预警待发送"
        # 触发 OpenClaw 通知（通过写入通知文件）
        echo "$(date -Iseconds): 股票预警触发，共 $ALERT_COUNT 条" >> /tmp/stock_alert_notifications.log
    fi
fi
