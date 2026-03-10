#!/bin/bash
# 设置股票价格预警 cron 任务

CRON_SCRIPT="/home/yctan/.openclaw/workspace-lead/stock_alert_cron.sh"
LOG_FILE="/home/yctan/.openclaw/workspace-lead/alerts.log"

# 创建 cron 执行脚本
cat > "$CRON_SCRIPT" << 'EOF'
#!/bin/bash
# 股票预警 cron 执行脚本

cd /home/yctan/.openclaw/workspace-lead

# 运行预警检查
output=$(python3 stock_alert.py 2>&1)

# 检查是否有预警
if echo "$output" | grep -q "===ALERTS_JSON==="; then
    # 提取 JSON 部分
    alerts_json=$(echo "$output" | sed -n '/===ALERTS_JSON===/,$p' | tail -n +2)
    
    # 发送飞书消息
    if [ -n "$alerts_json" ] && [ "$alerts_json" != "[]" ]; then
        # 解析 JSON 并发送每条预警
        echo "$alerts_json" | python3 -c "
import sys, json
alerts = json.load(sys.stdin)
for alert in alerts:
    print(alert)
" | while read -r message; do
            # 使用 feishu 发送消息（通过 openclaw message 工具）
            # 这里需要调用 openclaw 的 message 功能
            echo "$message" >> "$LOG_FILE"
            
            # 调用 openclaw 发送飞书消息
            /home/yctan/.npm-global/bin/openclaw message send --channel feishu --message "$message" 2>/dev/null
        done
    fi
fi
EOF

chmod +x "$CRON_SCRIPT"

# 添加 cron 任务（交易时段每 15 分钟）
# 上午：9:30-11:30 (30,45 分)
# 下午：13:00-15:00 (0,15,30,45 分)

# 备份当前 crontab
crontab -l > /tmp/crontab_backup.$$ 2>/dev/null || true

# 添加新的 cron 任务
(crontab -l 2>/dev/null | grep -v "stock_alert_cron.sh"; \
 echo "30,45 9 * * 1-5 $CRON_SCRIPT >> $LOG_FILE 2>&1"; \
 echo "0,15,30,45 10,11 * * 1-5 $CRON_SCRIPT >> $LOG_FILE 2>&1"; \
 echo "0,15,30,45 13,14 * * 1-5 $CRON_SCRIPT >> $LOG_FILE 2>&1"; \
 echo "0 15 * * 1-5 $CRON_SCRIPT >> $LOG_FILE 2>&1") | crontab -

echo "✓ Cron 任务已设置"
echo "交易时段每 15 分钟检查一次股票价格预警"
