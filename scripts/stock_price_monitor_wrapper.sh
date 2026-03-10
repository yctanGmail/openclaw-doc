#!/bin/bash
# 股票价格预警监控包装脚本
# 用于 cron 调用，处理预警推送

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/stock_price_monitor.py"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

cd "$WORKSPACE_DIR"

# 运行监控脚本并捕获输出
OUTPUT=$(python3 "$PYTHON_SCRIPT" 2>&1)

echo "$OUTPUT"

# 提取 JSON 格式的预警信息并推送
ALERTS=$(echo "$OUTPUT" | grep "^ALERT_JSON:" | sed 's/^ALERT_JSON://')

if [ -n "$ALERTS" ]; then
    # 逐条推送预警
    echo "$ALERTS" | while IFS= read -r alert_json; do
        if [ -n "$alert_json" ]; then
            # 使用 openclaw message 推送
            # 提取股票名称和建议
            stock_name=$(echo "$alert_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['stock'])")
            message=$(echo "$alert_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"🔔【价格预警】\\n股票：{d['stock']} ({d['code']})\\n现价：{d['price']:.2f} 元\\n涨跌：{d['change_pct']:+.2f}%\\n成本涨跌：{d['cost_change_pct']:+.2f}%\\n建议：{d['message']}\")")
            
            # 推送消息（通过 openclaw message 工具）
            # 注意：实际推送由 openclaw 的 message 工具处理
            echo "PUSH_TO_FEISHU:$message"
        fi
    done
fi
