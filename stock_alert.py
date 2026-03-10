#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票价格预警监控脚本
监控持仓股票，触发预警时推送消息
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
        "cost": 38.90
    },
    {
        "name": "紫金矿业",
        "code": "601899",
        "cost": 35.12
    }
]

# 预警阈值
ALERT_THRESHOLDS = [
    {"pct": 7, "type": "gain", "msg": "建议减仓", "level": "🔴"},
    {"pct": 5, "type": "gain", "msg": "考虑止盈", "level": "🟡"},
    {"pct": -8, "type": "loss", "msg": "考虑止损", "level": "🔴"},
    {"pct": -5, "type": "loss", "msg": "检查基本面", "level": "🟡"},
]

# 状态文件路径（用于记录已触发的预警，避免重复推送）
STATE_FILE = Path(__file__).parent / "stock_alert_state.json"

def load_state():
    """加载预警状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"triggered": {}}

def save_state(state):
    """保存预警状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_stock_price(code):
    """获取股票实时价格"""
    try:
        # 使用 akshare 获取实时行情
        if code.startswith('6'):
            # 沪市
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
        else:
            # 深市
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
        
        if stock.empty:
            return None, None, None
        
        current_price = float(stock.iloc[0]['最新价'])
        change_pct = float(stock.iloc[0]['涨跌幅'])
        prev_close = float(stock.iloc[0]['昨收'])
        
        return current_price, change_pct, prev_close
    except Exception as e:
        print(f"获取 {code} 价格失败：{e}")
        return None, None, None

def check_alerts():
    """检查所有持仓股票的预警"""
    state = load_state()
    alerts = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for stock in HOLDINGS:
        code = stock["code"]
        name = stock["name"]
        cost = stock["cost"]
        
        current_price, change_pct, prev_close = get_stock_price(code)
        
        if current_price is None:
            print(f"⚠️ 无法获取 {name}({code}) 的价格")
            continue
        
        # 计算相对于成本的涨跌幅
        cost_change_pct = ((current_price - cost) / cost) * 100
        
        # 检查预警阈值（按严重程度排序）
        triggered = False
        for threshold in sorted(ALERT_THRESHOLDS, key=lambda x: abs(x["pct"]), reverse=True):
            pct = threshold["pct"]
            
            # 判断是否触发
            if threshold["type"] == "gain" and cost_change_pct >= pct:
                # 检查是否已经触发过更高级别的预警
                alert_key = f"{code}_{pct}"
                if alert_key not in state["triggered"]:
                    alert_msg = f"{threshold['level']} 【价格预警】\n"
                    alert_msg += f"股票：{name}({code})\n"
                    alert_msg += f"现价：{current_price:.2f} 元\n"
                    alert_msg += f"较成本：{cost_change_pct:+.2f}%\n"
                    alert_msg += f"成本价：{cost:.2f} 元\n"
                    alert_msg += f"建议：{threshold['msg']}"
                    alerts.append(alert_msg)
                    state["triggered"][alert_key] = now
                    triggered = True
                break
            elif threshold["type"] == "loss" and cost_change_pct <= pct:
                alert_key = f"{code}_{pct}"
                if alert_key not in state["triggered"]:
                    alert_msg = f"{threshold['level']} 【价格预警】\n"
                    alert_msg += f"股票：{name}({code})\n"
                    alert_msg += f"现价：{current_price:.2f} 元\n"
                    alert_msg += f"较成本：{cost_change_pct:+.2f}%\n"
                    alert_msg += f"成本价：{cost:.2f} 元\n"
                    alert_msg += f"建议：{threshold['msg']}"
                    alerts.append(alert_msg)
                    state["triggered"][alert_key] = now
                    triggered = True
                break
        
        if not triggered:
            # 如果当前没有触发任何预警，清除该股票的已触发记录（允许再次触发）
            keys_to_remove = [k for k in state["triggered"] if k.startswith(code)]
            for k in keys_to_remove:
                del state["triggered"][k]
    
    # 保存状态
    save_state(state)
    
    return alerts

def is_trading_time():
    """检查是否在交易时间内"""
    from datetime import datetime
    now = datetime.now()
    
    # 检查是否是工作日
    if now.weekday() >= 5:  # 周六=5, 周日=6
        return False
    
    # 检查时间
    hour = now.hour
    minute = now.minute
    
    # 上午 9:30-11:30
    if hour == 9 and minute >= 30:
        return True
    if hour == 10 or (hour == 11 and minute <= 30):
        return True
    
    # 下午 13:00-15:00
    if hour == 13 or hour == 14 or (hour == 15 and minute <= 0):
        return True
    
    return False

if __name__ == "__main__":
    import sys
    
    # 检查是否启用测试模式（绕过交易时间检查）
    test_mode = "--test" in sys.argv
    
    # 检查是否在交易时间
    if not test_mode and not is_trading_time():
        print("⏰ 非交易时间，跳过检查")
        exit(0)
    
    mode_str = " [测试模式]" if test_mode else ""
    print(f"🔍 开始检查股票预警{mode_str} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    alerts = check_alerts()
    
    if alerts:
        print(f"\n🚨 触发 {len(alerts)} 条预警：")
        for alert in alerts:
            print("\n" + "="*40)
            print(alert)
            print("="*40 + "\n")
        
        # 输出警报标记，供 cron 调用时识别
        print("\n[ALERTS_TRIGGERED]")
        for alert in alerts:
            print(alert)
            print("---SPLIT---")
    else:
        print("✅ 无预警触发")
