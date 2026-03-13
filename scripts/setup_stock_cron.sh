#!/bin/bash
# 设置持仓股票价格预警 cron 任务
# 每 15 分钟检查一次（交易时间内脚本会自动跳过非交易时间）

CRON_SCRIPT="/home/yctan/.openclaw/workspace-lead/scripts/stock_price_monitor.py"
LOG_FILE="/home/yctan/.openclaw/workspace-lead/logs/stock_monitor.log"

# 创建日志目录
mkdir -p /home/yctan/.openclaw/workspace-lead/logs

# 添加到 crontab (每 15 分钟执行一次)
# 交易时间检查在脚本内部处理
(crontab -l 2>/dev/null | grep -v "stock_price_monitor.py"; echo "*/15 9-15 * * 1-5 cd /home/yctan/.openclaw/workspace-lead && /usr/bin/python3 $CRON_SCRIPT >> $LOG_FILE 2>&1") | crontab -

echo "✅ Cron 任务已设置：每 15 分钟检查持仓价格（仅在交易时间执行）"
echo "日志文件：$LOG_FILE"

# 显示当前 cron 任务
echo ""
echo "当前 cron 任务列表:"
crontab -l | grep stock
