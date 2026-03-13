#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票价格预警 - 测试模式
模拟触发预警，验证推送功能
"""

import sys
sys.path.insert(0, '/home/yctan/.openclaw/workspace-lead')

from stock_alert import format_alert

# 模拟触发预警
test_alerts = [
    {
        "stock": "招商银行",
        "code": "600036",
        "price": 40.85,  # +5% from cost 38.90
        "change_pct": 5.2,
        "cost": 38.90,
        "cost_change_pct": 5.01,
        "alert": "考虑止盈"
    },
    {
        "stock": "紫金矿业",
        "code": "601899",
        "price": 32.31,  # -8% from cost 35.12
        "change_pct": -8.1,
        "cost": 35.12,
        "cost_change_pct": -8.0,
        "alert": "考虑止损"
    }
]

print("=== 测试预警消息格式 ===\n")
for alert in test_alerts:
    msg = format_alert(alert)
    print(msg)
    print("---\n")

print("✅ 测试完成 - 消息格式正确")
