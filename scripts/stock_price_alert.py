#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股票价格预警监控脚本
监控招商银行和紫金矿业，触发预警时通过飞书推送
"""

import akshare as ak
import json
import os
from datetime import datetime
from pathlib import Path

# 持仓配置
HOLDINGS = [
    {
        "name": "招商银行",
        "code": "600036",
        "cost": 38.90,
        "exchange": "SH"
    },
    {
        "name": "紫金矿业",
        "code": "601899",
        "cost": 35.12,
        "exchange": "SH"
    }
]

# 预警阈值
ALERT_THRESHOLDS = [
    {"pct": 5, "type": "gain", "message": "考虑止盈"},
    {"pct": 7, "type": "gain", "message": "建议减仓"},
    {"pct": -5, "type": "drop", "message": "检查基本面"},
    {"pct": -8, "type": "drop", "message": "考虑止损"},
]

# 状态文件路径（用于避免重复推送）
STATE_FILE = Path(__file__).parent.parent / "memory" / "stock_alert_state.json"

def load_state():
    """加载上次预警状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_state(state):
    """保存预警状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_stock_price(code):
    """获取股票实时行情"""
    try:
        # 使用 akshare 获取实时行情
        if code.startswith('6'):
            # 沪市
            stock_code = f"sh{code}"
        else:
            # 深市
            stock_code = f"sz{code}"
        
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        stock_data = df[df['代码'] == code]
        
        if stock_data.empty:
            print(f"未找到股票 {code} 的数据")
            return None
        
        row = stock_data.iloc[0]
        current_price = float(row['最新价'])
        prev_close = float(row['昨收'])
        change_pct = float(row['涨跌幅'])
        
        return {
            "price": current_price,
            "prev_close": prev_close,
            "change_pct": change_pct
        }
    except Exception as e:
        print(f"获取行情失败：{e}")
        return None

def check_alerts(stock, price_data, last_alert_state):
    """检查是否触发预警"""
    alerts = []
    change_pct = price_data["change_pct"]
    current_price = price_data["price"]
    
    # 检查每个阈值
    for threshold in ALERT_THRESHOLDS:
        pct = threshold["pct"]
        alert_key = f"{stock['code']}_{pct}"
        
        # 判断是否触发
        triggered = False
        if threshold["type"] == "gain" and change_pct >= pct:
            triggered = True
        elif threshold["type"] == "drop" and change_pct <= pct:
            triggered = True
        
        # 如果触发且上次未推送此级别预警
        if triggered:
            # 检查是否已经推送过相同或更高级别的预警
            last_alert = last_alert_state.get(stock['code'], {})
            last_pct = last_alert.get('last_pct', -100)
            
            # 只在达到新的预警级别时推送
            if threshold["type"] == "gain" and pct > last_pct:
                alerts.append({
                    "stock": stock,
                    "price": current_price,
                    "change_pct": change_pct,
                    "message": threshold["message"],
                    "level": pct
                })
            elif threshold["type"] == "drop" and pct < last_pct:
                alerts.append({
                    "stock": stock,
                    "price": current_price,
                    "change_pct": change_pct,
                    "message": threshold["message"],
                    "level": pct
                })
            elif last_pct == -100:  # 首次预警
                alerts.append({
                    "stock": stock,
                    "price": current_price,
                    "change_pct": change_pct,
                    "message": threshold["message"],
                    "level": pct
                })
    
    return alerts

def format_alert_message(alert):
    """格式化预警消息"""
    stock = alert["stock"]
    price = alert["price"]
    change_pct = alert["change_pct"]
    suggestion = alert["message"]
    
    # 格式化涨跌幅显示
    if change_pct >= 0:
        change_str = f"+{change_pct:.2f}%"
    else:
        change_str = f"{change_pct:.2f}%"
    
    message = f"""🔔【价格预警】
股票：{stock['name']} ({stock['code']})
现价：{price:.2f} 元
涨跌：{change_str}
成本：{stock['cost']:.2f} 元
建议：{suggestion}"""
    
    return message

def send_feishu_alert(message):
    """通过飞书发送预警"""
    # 使用 OpenClaw 的 message 工具需要特殊处理
    # 这里输出到 stdout，由调用方处理
    print(f"FEISHU_ALERT:{message}")

def is_trading_time():
    """检查是否在交易时间内"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    # 检查是否是工作日
    if now.weekday() >= 5:  # 周六周日
        return False
    
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
    if hour == 15 and minute == 0:
        return True
    
    return False

def main():
    """主函数"""
    print(f"=== 股票价格预警检查 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查是否在交易时间
    if not is_trading_time():
        print("非交易时间，跳过检查")
        return
    
    # 加载上次状态
    state = load_state()
    last_date = state.get('last_date', '')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 如果是新的一天，重置状态
    if last_date != today:
        state = {'last_date': today, 'alerts': {}}
        print("新交易日，重置预警状态")
    
    alerts_triggered = []
    
    # 检查每只股票
    for stock in HOLDINGS:
        print(f"\n检查 {stock['name']} ({stock['code']})...")
        
        price_data = get_stock_price(stock['code'])
        if not price_data:
            continue
        
        print(f"  现价：{price_data['price']:.2f} 元")
        print(f"  涨跌：{price_data['change_pct']:.2f}%")
        
        # 检查预警
        stock_last_state = state.get('alerts', {}).get(stock['code'], {})
        alerts = check_alerts(stock, price_data, stock_last_state)
        
        if alerts:
            for alert in alerts:
                alerts_triggered.append(alert)
                msg = format_alert_message(alert)
                print(f"\n⚠️ 触发预警:")
                print(msg)
                send_feishu_alert(msg)
                
                # 更新状态
                if 'alerts' not in state:
                    state['alerts'] = {}
                state['alerts'][stock['code']] = {
                    'last_pct': alert['level'],
                    'last_time': datetime.now().isoformat()
                }
        else:
            print("  无预警触发")
    
    # 保存状态
    save_state(state)
    
    print(f"\n=== 检查完成，触发 {len(alerts_triggered)} 个预警 ===")

if __name__ == "__main__":
    main()
