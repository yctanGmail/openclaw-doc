#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送待处理的股票预警通知
由 OpenClaw 调用，通过 Feishu 发送消息
"""

import json
from pathlib import Path
from datetime import datetime

ALERT_FILE = Path(__file__).parent / "pending_alerts.json"

def send_pending_alerts():
    """读取并返回待发送的预警消息"""
    if not ALERT_FILE.exists():
        return []
    
    with open(ALERT_FILE, 'r', encoding='utf-8') as f:
        alerts = json.load(f)
    
    # 清空文件
    ALERT_FILE.write_text("[]", encoding='utf-8')
    
    return alerts

if __name__ == "__main__":
    alerts = send_pending_alerts()
    for alert in alerts:
        print(alert["message"])
        print("---")
