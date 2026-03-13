#!/bin/bash
# 股票预警监控包装脚本
# 执行 Python 脚本并处理预警输出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/stock_price_alert.py"

# 执行 Python 脚本并捕获输出
output=$(python3 "$PYTHON_SCRIPT" 2>&1)
echo "$output"

# 检查是否有预警触发
if echo "$output" | grep -q "ALERT_START"; then
    # 提取预警消息
    alert_message=$(echo "$output" | sed -n '/ALERT_START/,/ALERT_END/p' | grep -v "ALERT_")
    
    if [ -n "$alert_message" ]; then
        echo ""
        echo "=== 发送飞书消息 ==="
        
        # 使用 OpenClaw message 工具发送飞书消息
        # 通过 sessions_send 发送到主会话
        cat <<EOF
MESSAGE_START
$alert_message
MESSAGE_END
EOF
    fi
fi
