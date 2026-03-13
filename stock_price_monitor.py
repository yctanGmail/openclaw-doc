#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股票价格预警监控脚本
检查频率：每 15 分钟（交易时段 9:30-11:30, 13:00-15:00）
只在触发预警时推送
"""

import akshare as ak
import json
import os
from datetime import datetime
import requests

# 持仓配置
HOLDINGS = {
    "600036": {
        "name": "招商银行",
        "cost": 38.90
    },
    "601899": {
        "name": "紫金矿业",
        "cost": 35.12
    }
}

# 预警阈值
ALERT_THRESHOLDS = [
    {"pct": 7, "type": "gain", "message": "建议减仓"},
    {"pct": 5, "type": "gain", "message": "考虑止盈"},
    {"pct": -8, "type": "loss", "message": "考虑止损"},
    {"pct": -5, "type": "loss", "message": "检查基本面"},
]

# 状态文件路径（用于记录已触发的预警，避免重复推送）
STATE_FILE = os.path.join(os.path.dirname(__file__), "stock_alert_state.json")

# Feishu Webhook URL (从环境变量读取)
FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")


def load_state():
    """加载预警状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
            # 确保 alerts 键存在
            if "alerts" not in state:
                state["alerts"] = {}
            return state
    return {"alerts": {}}


def save_state(state):
    """保存预警状态"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_stock_price(stock_code):
    """使用 akshare 获取股票实时价格"""
    try:
        # akshare 获取 A 股实时行情
        stock_code_formatted = stock_code.lower()
        df = ak.stock_zh_a_spot_em()
        stock_data = df[df["代码"] == stock_code_formatted]
        
        if stock_data.empty:
            print(f"未找到股票 {stock_code} 的数据")
            return None
        
        current_price = float(stock_data["最新价"].iloc[0])
        change_pct = float(stock_data["涨跌幅"].iloc[0])
        
        return {
            "price": current_price,
            "change_pct": change_pct
        }
    except Exception as e:
        print(f"获取股票数据失败：{e}")
        return None


def check_alert(cost, current_price, change_pct):
    """检查是否触发预警"""
    # 计算相对于成本的涨跌幅
    cost_change_pct = ((current_price - cost) / cost) * 100
    
    for threshold in sorted(ALERT_THRESHOLDS, key=lambda x: abs(x["pct"]), reverse=True):
        if threshold["type"] == "gain" and cost_change_pct >= threshold["pct"]:
            return threshold["message"]
        elif threshold["type"] == "loss" and cost_change_pct <= threshold["pct"]:
            return threshold["message"]
    
    return None


def send_feishu_alert(stock_name, current_price, change_pct, suggestion):
    """发送飞书预警消息"""
    if not FEISHU_WEBHOOK_URL:
        print("未配置飞书 Webhook URL")
        return False
    
    # 根据涨跌设置颜色
    if change_pct > 0:
        color = "red"
        change_str = f"+{change_pct:.2f}%"
    elif change_pct < 0:
        color = "green"
        change_str = f"{change_pct:.2f}%"
    else:
        color = "gray"
        change_str = "0.00%"
    
    message = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🔔【价格预警】"
                },
                "template": "red" if change_pct > 0 else "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**股票：** {stock_name}\n**现价：** {current_price:.2f} 元\n**涨跌：** {change_str}\n**建议：** {suggestion}"
                    }
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            FEISHU_WEBHOOK_URL,
            json=message,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print(f"预警推送成功：{stock_name} - {suggestion}")
            return True
        else:
            print(f"预警推送失败：{response.status_code}")
            return False
    except Exception as e:
        print(f"发送飞书消息失败：{e}")
        return False


def is_trading_time():
    """检查是否在交易时段"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    # 周末不交易
    if weekday >= 5:
        return False
    
    # 上午交易时段 9:30-11:30
    if hour == 9 and minute >= 30:
        return True
    if hour == 10:
        return True
    if hour == 11 and minute <= 30:
        return True
    
    # 下午交易时段 13:00-15:00
    if hour == 13:
        return True
    if hour == 14:
        return True
    if hour == 15 and minute == 0:
        return True
    
    return False


def main():
    """主函数"""
    print(f"=== 股票价格预警检查 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ===")
    
    # 检查是否在交易时段
    if not is_trading_time():
        print("当前不在交易时段，跳过检查")
        return
    
    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today not in state["alerts"]:
        state["alerts"][today] = {}
    
    alerts_triggered = False
    
    for stock_code, stock_info in HOLDINGS.items():
        print(f"\n检查 {stock_info['name']} ({stock_code})...")
        
        # 获取实时价格
        data = get_stock_price(stock_code)
        if not data:
            continue
        
        current_price = data["price"]
        change_pct = data["change_pct"]
        cost = stock_info["cost"]
        
        print(f"  现价：{current_price:.2f} 元，涨跌幅：{change_pct:.2f}%")
        print(f"  成本：{cost:.2f} 元，相对成本涨跌：{((current_price - cost) / cost) * 100:.2f}%")
        
        # 检查预警
        suggestion = check_alert(cost, current_price, change_pct)
        
        if suggestion:
            alert_key = f"{stock_code}_{suggestion}"
            
            # 避免重复推送同一预警（同一天）
            if alert_key not in state["alerts"][today]:
                print(f"  ⚠️  触发预警：{suggestion}")
                
                # 发送飞书通知
                if send_feishu_alert(stock_info["name"], current_price, change_pct, suggestion):
                    state["alerts"][today][alert_key] = {
                        "time": datetime.now().isoformat(),
                        "price": current_price,
                        "suggestion": suggestion
                    }
                    alerts_triggered = True
            else:
                print(f"  ℹ️  预警已推送过：{suggestion}")
        else:
            print(f"  ✓  无预警")
    
    # 保存状态
    save_state(state)
    
    print(f"\n=== 检查完成 {'(有预警)' if alerts_triggered else '(无预警)'} ===")


if __name__ == "__main__":
    main()
