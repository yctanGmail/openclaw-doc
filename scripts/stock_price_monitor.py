#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股票价格预警监控脚本
- 每 15 分钟检查一次持仓股票
- 触发预警条件时通过飞书推送
"""

import akshare as ak
import json
import os
from datetime import datetime
from pathlib import Path

# 持仓配置
HOLDINGS = [
    {"code": "600036", "name": "招商银行", "cost": 38.90},
    {"code": "601899", "name": "紫金矿业", "cost": 35.12},
]

# 预警阈值
ALERT_THRESHOLDS = [
    {"pct": 7, "level": "high_profit", "message": "建议减仓"},
    {"pct": 5, "level": "profit", "message": "考虑止盈"},
    {"pct": -8, "level": "high_loss", "message": "考虑止损"},
    {"pct": -5, "level": "loss", "message": "检查基本面"},
]

# 状态文件路径
STATE_FILE = Path(__file__).parent.parent / "data" / "stock_monitor_state.json"

def get_current_price(code: str) -> float:
    """获取股票实时价格"""
    try:
        # 使用 akshare 获取实时行情
        stock_info = ak.stock_zh_a_spot_em()
        stock = stock_info[stock_info['代码'] == code]
        if len(stock) > 0:
            return float(stock.iloc[0]['最新价'])
        return None
    except Exception as e:
        print(f"获取 {code} 价格失败：{e}")
        return None

def load_state() -> dict:
    """加载监控状态"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"alerts": {}}

def save_state(state: dict):
    """保存监控状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def check_alerts():
    """检查所有持仓股票的预警条件"""
    state = load_state()
    alerts_to_send = []
    
    for stock in HOLDINGS:
        code = stock["code"]
        name = stock["name"]
        cost = stock["cost"]
        
        current_price = get_current_price(code)
        if current_price is None:
            print(f"跳过 {name} - 无法获取价格")
            continue
        
        # 计算涨跌幅
        pct_change = ((current_price - cost) / cost) * 100
        
        # 检查预警条件（从高到低，只触发最严重的）
        triggered_alert = None
        for threshold in sorted(ALERT_THRESHOLDS, key=lambda x: abs(x["pct"]), reverse=True):
            if threshold["pct"] > 0 and pct_change >= threshold["pct"]:
                triggered_alert = threshold
                break
            elif threshold["pct"] < 0 and pct_change <= threshold["pct"]:
                triggered_alert = threshold
                break
        
        if triggered_alert:
            alert_key = f"{code}_{triggered_alert['level']}"
            alert_id = f"{code}_{triggered_alert['level']}_{int(current_price * 100)}"
            
            # 避免重复推送相同价格区间的预警
            if state["alerts"].get(alert_key) != alert_id:
                state["alerts"][alert_key] = alert_id
                
                alert_msg = {
                    "stock": name,
                    "code": code,
                    "price": current_price,
                    "pct": pct_change,
                    "suggestion": triggered_alert["message"]
                }
                alerts_to_send.append(alert_msg)
                
                print(f"🔔 触发预警：{name} 现价{current_price:.2f} 涨跌{pct_change:+.2f}% - {triggered_alert['message']}")
        else:
            # 价格回到正常区间，清除预警状态
            for key in list(state["alerts"].keys()):
                if key.startswith(f"{code}_"):
                    del state["alerts"][key]
    
    save_state(state)
    return alerts_to_send

def is_trading_time() -> bool:
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
    if hour == 11 and minute <= 30:
        return True
    
    # 下午 13:00-15:00
    if hour == 13:
        return True
    if hour == 14:
        return True
    if hour == 15 and minute <= 0:
        return True
    
    return False

def main():
    """主函数"""
    import sys
    
    # 检查是否在交易时间（除非使用 --test 强制测试）
    force_test = "--test" in sys.argv
    if not force_test and not is_trading_time():
        print(f"非交易时间，跳过检查 - {datetime.now()}")
        return
    
    print(f"开始检查持仓价格 - {datetime.now()}")
    alerts = check_alerts()
    
    if alerts:
        # 输出需要推送的预警（由外部脚本处理推送）
        print(f"\n需要推送 {len(alerts)} 条预警:")
        for alert in alerts:
            # 输出 JSON 格式，便于外部脚本解析
            print(json.dumps(alert, ensure_ascii=False))
    else:
        print("无预警触发")

if __name__ == "__main__":
    main()
