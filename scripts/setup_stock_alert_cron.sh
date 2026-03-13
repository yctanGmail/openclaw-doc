#!/bin/bash
# 设置股票预警监控的 cron 任务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_SCRIPT="$SCRIPT_DIR/stock_alert_wrapper.sh"

# 使脚本可执行
chmod +x "$WRAPPER_SCRIPT"
chmod +x "$SCRIPT_DIR/stock_price_alert.py"

# 显示当前 crontab
echo "当前 crontab:"
crontab -l 2>/dev/null || echo "(空)"

echo ""
echo "=== 添加股票预警监控任务 ==="
echo "交易时间每 15 分钟检查一次："
echo "  上午：9:30-11:30"
echo "  下午：13:00-15:00"

# 创建新的 crontab 条目
CRON_ENTRIES="
# 股票价格预警监控 - 上午场 (9:30-11:30)
30 9 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
45 9 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
0 10 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
15 10 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
30 10 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
45 10 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
0 11 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
15 11 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1

# 股票价格预警监控 - 下午场 (13:00-15:00)
0 13 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
15 13 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
30 13 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
45 13 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
0 14 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
15 14 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
30 14 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
45 14 * * 1-5 $WRAPPER_SCRIPT >> /tmp/stock_alert.log 2>&1
"

# 添加到 crontab
(crontab -l 2>/dev/null | grep -v "股票价格预警监控"; echo "$CRON_ENTRIES") | crontab -

echo ""
echo "✅ cron 任务已添加！"
echo ""
echo "查看日志：tail -f /tmp/stock_alert.log"
echo "测试运行：$WRAPPER_SCRIPT"
