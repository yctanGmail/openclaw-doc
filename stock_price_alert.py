#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票价格预警监控脚本
监控持仓股票价格，触发预警条件时推送飞书消息
"""

import akshare as ak
import requests
import json
import os
from datetime import datetime

# 持仓配置
HOLDINGS = [
    {"name": "招商银行", "code": "600036", "cost": 38.90},
    {"name": "紫金矿业", "code": "601899", "cost": 35.12},
]

# 预警阈值
ALERT_THRESHOLDS = [
    {"threshold": 7, "type": "gain", "message": "建议减仓"},
    {"threshold": 5, "type": "gain", "message": "考虑止盈"},
    {"threshold": -8, "type": "loss", "message": "考虑止损"},
    {"threshold": -5, "type": "loss", "message": "检查基本面"},
]

# 状态文件路径（用于记录已触发的预警，避免重复推送）
STATE_FILE = "/home/yctan/.openclaw/workspace-lead/alert_state.json"

def load_state():
    """加载预警状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_state(state):
    """保存预警状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_stock_price(code):
    """获取股票实时价格"""
    try:
        # 使用 akshare 获取实时行情
        if code.startswith('6'):
            # 沪市股票
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            if len(stock) > 0:
                return {
                    "price": float(stock.iloc[0]['最新价']),
                    "change_percent": float(stock.iloc[0]['涨跌幅']),
                    "name": stock.iloc[0]['名称']
                }
        else:
            # 深市股票
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            if len(stock) > 0:
                return {
                    "price": float(stock.iloc[0]['最新价']),
                    "change_percent": float(stock.iloc[0]['涨跌幅']),
                    "name": stock.iloc[0]['名称']
                }
    except Exception as e:
        print(f"获取股票 {code} 价格失败：{e}")
    return None

def check_alert(stock_info, holding, state):
    """检查是否触发预警"""
    change = stock_info["change_percent"]
    cost = holding["cost"]
    current_price = stock_info["price"]
    
    # 计算相对于成本的涨跌幅
    cost_change = ((current_price - cost) / cost) * 100
    
    # 生成唯一键用于状态追踪
    alert_key = f"{holding['code']}_{holding['name']}"
    
    # 按严重程度检查预警（从最严重开始）
    for threshold_config in ALERT_THRESHOLDS:
        threshold = threshold_config["threshold"]
        message = threshold_config["message"]
        
        # 检查是否触发
        triggered = False
        if threshold > 0 and cost_change >= threshold:
            triggered = True
        elif threshold < 0 and cost_change <= threshold:
            triggered = True
        
        if triggered:
            # 检查是否已经推送过（避免重复）
            last_alert = state.get(alert_key, {}).get("last_alert", "")
            if last_alert != message:
                # 需要推送新预警
                return {
                    "stock_name": holding["name"],
                    "code": holding["code"],
                    "current_price": current_price,
                    "cost": cost,
                    "change_percent": cost_change,
                    "daily_change": change,
                    "alert_message": message,
                    "alert_key": alert_key
                }
            else:
                # 已经推送过相同预警，跳过
                return None
    
    return None

def send_feishu_alert(alert_info):
    """发送飞书预警消息"""
    # 从环境变量获取飞书 webhook
    webhook_url = os.environ.get("FEISHU_WEBHOOK")
    if not webhook_url:
        print("未配置 FEISHU_WEBHOOK 环境变量")
        return False
    
    content = f"""🔔【价格预警】
股票：{alert_info['stock_name']}({alert_info['code']})
现价：{alert_info['current_price']:.2f} 元
成本：{alert_info['cost']:.2f} 元
涨跌：{alert_info['change_percent']:+.2f}%
建议：{alert_info['alert_message']}

时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": content
        }
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"预警推送成功：{alert_info['stock_name']} - {alert_info['alert_message']}")
            return True
        else:
            print(f"预警推送失败：{response.status_code}")
            return False
    except Exception as e:
        print(f"发送飞书消息失败：{e}")
        return False

def main():
    """主函数"""
    print(f"开始检查股票价格预警 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载状态
    state = load_state()
    alerts_triggered = []
    
    for holding in HOLDINGS:
        print(f"检查 {holding['name']}({holding['code']})...")
        stock_info = get_stock_price(holding["code"])
        
        if stock_info:
            print(f"  现价：{stock_info['price']:.2f}元，涨跌幅：{stock_info['change_percent']:.2f}%")
            alert = check_alert(stock_info, holding, state)
            
            if alert:
                print(f"  ⚠️ 触发预警：{alert['alert_message']}")
                if send_feishu_alert(alert):
                    # 更新状态
                    if alert['alert_key'] not in state:
                        state[alert['alert_key']] = {}
                    state[alert['alert_key']]["last_alert"] = alert['alert_message']
                    state[alert['alert_key']]["last_time"] = datetime.now().isoformat()
                    alerts_triggered.append(alert)
        else:
            print(f"  无法获取价格数据")
    
    # 保存状态
    save_state(state)
    
    # 如果没有触发预警，检查是否需要清除状态（价格回到安全区间）
    for holding in HOLDINGS:
        alert_key = f"{holding['code']}_{holding['name']}"
        if alert_key in state:
            stock_info = get_stock_price(holding["code"])
            if stock_info:
                cost_change = ((stock_info["price"] - holding["cost"]) / holding["cost"]) * 100
                # 如果涨跌幅回到 -3% 到 +3% 之间，清除预警状态
                if -3 <= cost_change <= 3:
                    print(f"  {holding['name']} 价格回到安全区间，清除预警状态")
                    del state[alert_key]
    
    save_state(state)
    
    if not alerts_triggered:
        print("无新预警触发")
    
    print("检查完成")

if __name__ == "__main__":
    main()
