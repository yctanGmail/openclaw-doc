#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票价格预警监控脚本
监控持仓股票，触发预警条件时推送飞书消息
"""

import akshare as ak
import json
import os
from datetime import datetime
import subprocess

# 持仓配置
HOLDINGS = [
    {
        "name": "招商银行",
        "code": "600036",
        "cost": 38.90,
        "market": "sh"
    },
    {
        "name": "紫金矿业",
        "code": "601899",
        "cost": 35.12,
        "market": "sh"
    }
]

# 预警条件
ALERT_THRESHOLDS = [
    {"pct": 5, "type": "gain", "message": "考虑止盈"},
    {"pct": 7, "type": "gain", "message": "建议减仓"},
    {"pct": -5, "type": "loss", "message": "检查基本面"},
    {"pct": -8, "type": "loss", "message": "考虑止损"},
]

# 状态文件路径（用于记录已触发的预警，避免重复推送）
STATE_FILE = os.path.join(os.path.dirname(__file__), "stock_alert_state.json")

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
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == code]
        if len(stock) == 0:
            return None
        
        current_price = float(stock['最新价'].iloc[0])
        prev_close = float(stock['昨收'].iloc[0])
        change_pct = float(stock['涨跌幅'].iloc[0])
        
        return {
            "price": current_price,
            "prev_close": prev_close,
            "change_pct": change_pct
        }
    except Exception as e:
        print(f"获取 {code} 价格失败：{e}")
        return None

def check_alert(stock, price_info, state):
    """检查是否触发预警（相对于成本价）"""
    current_price = price_info["price"]
    daily_change_pct = price_info["change_pct"]
    cost = stock["cost"]
    
    # 计算相对于成本价的涨跌幅
    cost_change_pct = ((current_price - cost) / cost) * 100
    
    # 生成预警键（基于预警消息，避免重复推送相同预警）
    alert_key = None
    alert_message = None
    
    # 按严重程度检查预警（从最严重开始）
    for threshold in ALERT_THRESHOLDS:
        triggered = False
        if threshold["type"] == "gain" and cost_change_pct >= threshold["pct"]:
            triggered = True
            alert_message = threshold["message"]
        elif threshold["type"] == "loss" and cost_change_pct <= threshold["pct"]:
            triggered = True
            alert_message = threshold["message"]
        
        if triggered:
            alert_key = f"{stock['code']}_{alert_message}"
            # 检查是否已推送过此预警
            if alert_key not in state.get(stock['code'], []):
                return {
                    "stock": stock["name"],
                    "code": stock["code"],
                    "price": current_price,
                    "cost": cost,
                    "change_pct": cost_change_pct,
                    "daily_change_pct": daily_change_pct,
                    "message": alert_message,
                    "alert_key": alert_key
                }
            else:
                # 已推送过相同预警，跳过
                return None
    
    return None

def send_feishu_alert(alert):
    """发送飞书预警消息"""
    message = f"""🔔【价格预警】
股票：{alert['stock']}({alert['code']})
现价：{alert['price']:.2f} 元
涨跌：{alert['change_pct']:+.2f}%
建议：{alert['message']}"""
    
    print(message)
    
    # 使用 openclaw message 发送飞书消息
    try:
        subprocess.run([
            "npx", "-y", "openclaw", "message", "send",
            "--channel", "feishu",
            "--message", message
        ], check=True, capture_output=True)
        print("✓ 预警已推送")
    except Exception as e:
        print(f"推送失败：{e}")

def is_trading_time():
    """检查是否在交易时间内"""
    now = datetime.now()
    weekday = now.weekday()
    
    # 周末不交易
    if weekday >= 5:
        return False
    
    hour = now.hour
    minute = now.minute
    
    # 上午 9:30-11:30
    if hour == 9 and minute >= 30:
        return True
    if hour == 10:
        return True
    if hour == 11 and minute < 30:
        return True
    
    # 下午 13:00-15:00
    if hour == 13:
        return True
    if hour == 14:
        return True
    if hour == 15 and minute == 0:
        return True
    
    return False

def main():
    """主函数"""
    # 检查是否在交易时间
    if not is_trading_time():
        print("非交易时间，跳过检查")
        return
    
    print(f"开始检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载状态
    state = load_state()
    alerts_sent = False
    
    for stock in HOLDINGS:
        print(f"检查 {stock['name']}({stock['code']})...")
        
        price_info = get_stock_price(stock["code"])
        if not price_info:
            continue
        
        print(f"  现价：{price_info['price']:.2f}, 涨跌：{price_info['change_pct']:+.2f}%")
        
        alert = check_alert(stock, price_info, state)
        if alert:
            send_feishu_alert(alert)
            alerts_sent = True
            
            # 记录已推送的预警
            if stock["code"] not in state:
                state[stock["code"]] = []
            state[stock["code"]].append(f"{stock['code']}_{int(alert['change_pct'])}")
    
    # 保存状态
    save_state(state)
    
    # 如果是新的一天，清空状态（允许重新预警）
    today = datetime.now().strftime('%Y-%m-%d')
    if state.get('_last_date') != today:
        state.clear()
        state['_last_date'] = today
        save_state(state)
    
    if not alerts_sent:
        print("无预警触发")

if __name__ == "__main__":
    main()
