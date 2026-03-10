#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股票价格预警监控脚本
检查频率：每 15 分钟（交易时段 9:30-11:30, 13:00-15:00）
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
THRESHOLDS = [
    {"pct": 7, "type": "up", "message": "建议减仓"},
    {"pct": 5, "type": "up", "message": "考虑止盈"},
    {"pct": -5, "type": "down", "message": "检查基本面"},
    {"pct": -8, "type": "down", "message": "考虑止损"},
]

# 状态文件路径（用于避免重复推送）
STATE_FILE = Path(__file__).parent.parent / "data" / "stock_monitor_state.json"
STATE_FILE.parent.mkdir(exist_ok=True)


def load_state():
    """加载上次预警状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    """保存预警状态"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_stock_price(code):
    """获取股票实时价格"""
    try:
        # 使用 akshare 获取实时行情
        if code.startswith("6"):
            # 沪市
            stock_df = ak.stock_zh_a_spot_em()
            stock_info = stock_df[stock_df["代码"] == code]
        else:
            # 深市
            stock_df = ak.stock_zh_a_spot_em()
            stock_info = stock_df[stock_df["代码"] == code]
        
        if stock_info.empty:
            print(f"未找到股票 {code}")
            return None
        
        row = stock_info.iloc[0]
        current_price = float(row["最新价"])
        change_pct = float(row["涨跌幅"])
        
        return {
            "price": current_price,
            "change_pct": change_pct,
        }
    except Exception as e:
        print(f"获取 {code} 价格失败：{e}")
        return None


def check_alerts():
    """检查所有持仓股票的预警"""
    state = load_state()
    alerts = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for stock in HOLDINGS:
        code = stock["code"]
        name = stock["name"]
        cost = stock["cost"]
        
        # 获取实时数据
        data = get_stock_price(code)
        if not data:
            continue
        
        current_price = data["price"]
        change_pct = data["change_pct"]
        
        # 计算相对于成本的涨跌幅
        cost_change_pct = ((current_price - cost) / cost) * 100
        
        # 检查预警阈值（按严重程度排序）
        triggered = None
        for threshold in sorted(THRESHOLDS, key=lambda x: abs(x["pct"]), reverse=True):
            pct = threshold["pct"]
            if pct > 0 and cost_change_pct >= pct:
                triggered = threshold
                break
            elif pct < 0 and cost_change_pct <= pct:
                triggered = threshold
                break
        
        # 生成唯一标识
        alert_key = f"{code}_{triggered['pct']}" if triggered else f"{code}_normal"
        last_alert = state.get(code, {}).get("last_alert")
        
        # 只在触发新预警或状态变化时推送
        if triggered:
            if last_alert != alert_key:
                alerts.append({
                    "stock": name,
                    "code": code,
                    "price": current_price,
                    "change_pct": change_pct,
                    "cost_change_pct": cost_change_pct,
                    "message": triggered["message"],
                })
                # 更新状态
                if code not in state:
                    state[code] = {}
                state[code]["last_alert"] = alert_key
                state[code]["last_check"] = now
        else:
            # 恢复正常状态
            if last_alert and last_alert != alert_key:
                if code not in state:
                    state[code] = {}
                state[code]["last_alert"] = alert_key
                state[code]["last_check"] = now
    
    save_state(state)
    return alerts


def format_alert(alert):
    """格式化预警消息"""
    return f"""🔔【价格预警】
股票：{alert['stock']} ({alert['code']})
现价：{alert['price']:.2f} 元
涨跌：{alert['change_pct']:+.2f}%
成本涨跌：{alert['cost_change_pct']:+.2f}%
建议：{alert['message']}"""


def main():
    """主函数"""
    # 检查是否在交易时段
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    # 交易时段判断
    is_trading_time = False
    if 9 <= hour <= 11:
        if hour == 9 and minute >= 30:
            is_trading_time = True
        elif hour == 11 and minute <= 30:
            is_trading_time = True
        elif 10 <= hour <= 10:
            is_trading_time = True
    elif 13 <= hour <= 15:
        if hour == 15 and minute <= 0:
            is_trading_time = True
        elif 13 <= hour <= 14:
            is_trading_time = True
    
    if not is_trading_time:
        print(f"非交易时段，跳过检查 (当前时间：{now.strftime('%H:%M')})")
        return
    
    print(f"开始检查价格预警 (当前时间：{now.strftime('%Y-%m-%d %H:%M')})")
    
    alerts = check_alerts()
    
    if alerts:
        print(f"触发 {len(alerts)} 个预警")
        for alert in alerts:
            message = format_alert(alert)
            print(message)
            print("---")
            # 输出 JSON 格式供外部调用
            print(f"ALERT_JSON:{json.dumps(alert, ensure_ascii=False)}")
    else:
        print("无预警触发")


if __name__ == "__main__":
    main()
