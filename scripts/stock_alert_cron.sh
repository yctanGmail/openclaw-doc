#!/bin/bash
# 股票价格预警 Cron 包装脚本
# 执行 Python 脚本并处理预警输出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/stock_price_alert.py"
LOG_FILE="$SCRIPT_DIR/../memory/stock_alert.log"

# 执行 Python 脚本
OUTPUT=$(python3 "$PYTHON_SCRIPT" 2>&1)

# 记录日志
echo "=== $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
echo "$OUTPUT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 检查是否有预警触发
if echo "$OUTPUT" | grep -q "---ALERT_TRIGGERED---"; then
    # 提取预警消息（去掉标记行）
    ALERT_MSG=$(echo "$OUTPUT" | grep -v "---ALERT_TRIGGERED---" | grep -v "检查完成")
    
    # 通过 OpenClaw 发送飞书消息
    # 使用 message 工具发送到当前会话
    echo "$ALERT_MSG" | openclaw message send --channel feishu --message "$(cat)"
    
    echo "预警已发送到飞书" >> "$LOG_FILE"
fi
