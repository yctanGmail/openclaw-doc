#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票预警逻辑（模拟数据）
"""

# 模拟测试预警逻辑
HOLDINGS = [
    {"code": "600036", "name": "招商银行", "cost": 38.90},
    {"code": "601899", "name": "紫金矿业", "cost": 35.12},
]

ALERT_THRESHOLDS = [
    {"pct": 5, "type": "up", "message": "考虑止盈"},
    {"pct": 7, "type": "up", "message": "建议减仓"},
    {"pct": -5, "type": "down", "message": "检查基本面"},
    {"pct": -8, "type": "down", "message": "考虑止损"},
]

def check_alert(current_price, cost):
    cost_change_pct = ((current_price - cost) / cost) * 100
    
    alerts = []
    for threshold in ALERT_THRESHOLDS:
        if threshold["type"] == "up" and cost_change_pct >= threshold["pct"]:
            alerts.append({"level": threshold["pct"], "type": "up", "message": threshold["message"]})
        elif threshold["type"] == "down" and cost_change_pct <= threshold["pct"]:
            alerts.append({"level": threshold["pct"], "type": "down", "message": threshold["message"]})
    
    # 返回最严重的预警
    if alerts:
        if alerts[0]["type"] == "up":
            return cost_change_pct, [max(alerts, key=lambda x: x["level"])]
        else:
            return cost_change_pct, [min(alerts, key=lambda x: x["level"])]
    return cost_change_pct, []

print("=== 股票预警逻辑测试 ===\n")

for holding in HOLDINGS:
    print(f"{holding['name']} ({holding['code']}) - 成本：{holding['cost']:.2f}元")
    
    # 测试不同价格场景
    test_prices = [
        (holding['cost'] * 1.08, "大涨 8%"),
        (holding['cost'] * 1.06, "大涨 6%"),
        (holding['cost'], "持平"),
        (holding['cost'] * 0.94, "大跌 6%"),
        (holding['cost'] * 0.90, "大跌 10%"),
    ]
    
    for price, scenario in test_prices:
        pct, alerts = check_alert(price, holding['cost'])
        alert_msg = alerts[0]["message"] if alerts else "无预警"
        print(f"  {scenario}: 现价{price:.2f}元, 涨跌{pct:+.1f}% → {alert_msg}")
    
    print()
