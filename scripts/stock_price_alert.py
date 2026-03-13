#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票价格预警监控脚本
监控持仓股票价格，触发预警条件时推送飞书消息
"""

import akshare as ak
import json
import os
from datetime import datetime
from pathlib import Path

# 配置
HOLDINGS = [
    {"code": "600036", "name": "招商银行", "cost": 38.90},
    {"code": "601899", "name": "紫金矿业", "cost": 35.12},
]

# 预警阈值
ALERT_THRESHOLDS = [
    {"pct": 5, "type": "up", "message": "考虑止盈"},
    {"pct": 7, "type": "up", "message": "建议减仓"},
    {"pct": -5, "type": "down", "message": "检查基本面"},
    {"pct": -8, "type": "down", "message": "考虑止损"},
]

# 状态文件路径（用于记录已触发的预警，避免重复推送）
STATE_FILE = Path(__file__).parent.parent / "data" / "stock_alert_state.json"


def get_stock_price(code: str) -> dict:
    """获取股票实时价格"""
    try:
        # 使用 akshare 获取实时行情
        stock_info = ak.stock_zh_a_spot_em()
        stock = stock_info[stock_info['代码'] == code]
        
        if stock.empty:
            return None
        
        row = stock.iloc[0]
        return {
            "code": code,
            "name": row.get('名称', ''),
            "price": float(row.get('最新价', 0)),
            "change_pct": float(row.get('涨跌幅', 0)),
            "change": float(row.get('涨跌额', 0)),
        }
    except Exception as e:
        print(f"获取 {code} 价格失败：{e}")
        return None


def check_alert(stock: dict, cost: float) -> list:
    """检查是否触发预警 - 返回最严重的预警级别"""
    current_price = stock["price"]
    # 计算相对于成本价的涨跌幅
    cost_change_pct = ((current_price - cost) / cost) * 100
    
    alerts = []
    for threshold in ALERT_THRESHOLDS:
        if threshold["type"] == "up" and cost_change_pct >= threshold["pct"]:
            alerts.append({
                "level": threshold["pct"],
                "direction": "up",
                "message": threshold["message"],
                "cost_change_pct": cost_change_pct,
            })
        elif threshold["type"] == "down" and cost_change_pct <= threshold["pct"]:
            alerts.append({
                "level": threshold["pct"],
                "direction": "down",
                "message": threshold["message"],
                "cost_change_pct": cost_change_pct,
            })
    
    # 返回最严重的预警（上涨取最高阈值，下跌取最低阈值）
    if alerts:
        if alerts[0]["direction"] == "up":
            # 上涨：返回阈值最高的（最严重）
            return [max(alerts, key=lambda x: x["level"])]
        else:
            # 下跌：返回阈值最低的（最严重，如 -8% 比 -5% 更严重）
            return [min(alerts, key=lambda x: x["level"])]
    return []


def load_state() -> dict:
    """加载状态文件"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_state(state: dict):
    """保存状态文件"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def should_alert(stock_code: str, alert_level: int, direction: str, state: dict) -> bool:
    """判断是否应该推送（避免重复推送同一级别的预警）"""
    key = f"{stock_code}_{direction}_{alert_level}"
    
    # 如果这个级别的预警已经推送过，且当前没有更严重的预警，则不推送
    last_alert = state.get(key)
    if last_alert:
        # 检查是否是新的交易日
        last_date = last_alert.get("date", "")
        today = datetime.now().strftime("%Y-%m-%d")
        if last_date == today:
            return False
    
    return True


def format_alert_message(stock: dict, cost: float, alert: dict) -> str:
    """格式化预警消息"""
    cost_change_pct = alert["cost_change_pct"]
    direction_symbol = "+" if cost_change_pct >= 0 else ""
    
    return f"""🔔【价格预警】
股票：{stock['name']} ({stock['code']})
现价：{stock['price']:.2f} 元
成本：{cost:.2f} 元
涨跌：{direction_symbol}{cost_change_pct:.1f}% (相对成本)
建议：{alert['message']}"""


def send_feishu_alert(message: str):
    """发送飞书消息（通过 OpenClaw message 工具）"""
    # 这个函数会被 OpenClaw 调用，实际发送通过 message 工具
    # 这里只打印消息，由调用方处理发送
    print("FEISHU_ALERT:" + message)


def main():
    """主函数"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    
    # 检查是否在交易时间
    if not ((9, 30) <= (now.hour, now.minute) <= (11, 30) or 
            (13, 0) <= (now.hour, now.minute) <= (15, 0)):
        print(f"非交易时间 ({current_time})，跳过检查")
        return
    
    # 检查是否是交易日（简单判断：工作日）
    weekday = now.weekday()
    if weekday >= 5:  # 周六=5, 周日=6
        print(f"周末，跳过检查")
        return
    
    state = load_state()
    alerts_triggered = []
    
    for holding in HOLDINGS:
        code = holding["code"]
        name = holding["name"]
        cost = holding["cost"]
        
        print(f"检查 {name} ({code})...")
        
        stock = get_stock_price(code)
        if not stock:
            print(f"  获取价格失败")
            continue
        
        print(f"  现价：{stock['price']:.2f} 元，涨跌幅：{stock['change_pct']:.2f}%")
        
        alerts = check_alert(stock, cost)
        if alerts:
            alert = alerts[0]
            direction = alert["direction"]
            level = alert["level"]
            
            if should_alert(code, level, direction, state):
                message = format_alert_message(stock, cost, alert)
                alerts_triggered.append({
                    "stock": name,
                    "code": code,
                    "message": message,
                })
                
                # 更新状态
                key = f"{code}_{direction}_{level}"
                state[key] = {
                    "date": today,
                    "time": current_time,
                    "price": stock["price"],
                }
    
    # 保存状态
    save_state(state)
    
    # 输出结果
    if alerts_triggered:
        print(f"\n触发 {len(alerts_triggered)} 个预警:")
        for alert in alerts_triggered:
            print(f"\n{alert['message']}")
            print("FEISHU_ALERT:" + alert['message'])
    else:
        print("\n无预警触发")
    
    # 输出 JSON 结果供调用方解析
    result = {
        "timestamp": now.isoformat(),
        "alerts": alerts_triggered,
    }
    print(f"\nRESULT_JSON:{json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
