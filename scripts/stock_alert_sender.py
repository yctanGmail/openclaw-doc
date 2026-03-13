#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股票预警推送脚本
- 调用监控脚本获取预警信息
- 通过 OpenClaw message 工具推送到飞书
"""

import subprocess
import json
import sys

def send_feishu_alert(alert: dict):
    """发送飞书预警消息"""
    stock = alert["stock"]
    code = alert["code"]
    price = alert["price"]
    pct = alert["pct"]
    suggestion = alert["suggestion"]
    
    # 根据涨跌设置 emoji
    if pct > 0:
        emoji = "📈"
        pct_str = f"+{pct:.2f}%"
    else:
        emoji = "📉"
        pct_str = f"{pct:.2f}%"
    
    # 构建消息
    message = f"""🔔【价格预警】
{emoji} 股票：{stock} ({code})
💰 现价：{price:.2f} 元
📊 涨跌：{pct_str}
💡 建议：{suggestion}"""
    
    print(message)
    print("---")
    print(f"OPENCLAW_MESSAGE:{json.dumps({'text': message, 'channel': 'feishu'})}")

def main():
    # 运行监控脚本
    result = subprocess.run(
        ["python3", "/home/yctan/.openclaw/workspace-lead/scripts/stock_price_monitor.py"],
        capture_output=True,
        text=True
    )
    
    output = result.stdout
    lines = output.strip().split('\n')
    
    alerts_found = False
    for line in lines:
        if line.startswith('{') and line.endswith('}'):
            try:
                alert = json.loads(line)
                send_feishu_alert(alert)
                alerts_found = True
            except json.JSONDecodeError:
                pass
    
    if not alerts_found:
        print("无预警需要推送")
        sys.exit(0)

if __name__ == "__main__":
    main()
