#!/usr/bin/env python3
"""
持仓股票价格预警监控脚本
检查频率：每 15 分钟（9:30-11:30, 13:00-15:00）
"""

import akshare as ak
import json
from datetime import datetime

# 持仓配置
HOLDINGS = [
    {"code": "600036", "name": "招商银行", "cost": 38.90},
    {"code": "601899", "name": "紫金矿业", "cost": 35.12},
]

# 预警阈值
THRESHOLDS = [
    {"pct": 7, "type": "gain", "message": "建议减仓"},
    {"pct": 5, "type": "gain", "message": "考虑止盈"},
    {"pct": -8, "type": "loss", "message": "考虑止损"},
    {"pct": -5, "type": "loss", "message": "检查基本面"},
]

def get_stock_price(code):
    """获取股票实时价格"""
    try:
        # 获取个股实时行情 - 使用更可靠的接口
        df = ak.stock_zh_a_hist(symbol=code, period="1m", adjust="qfq")
        if len(df) == 0:
            return None
        
        # 获取最新一条数据
        latest = df.iloc[-1]
        current_price = float(latest['收盘'])
        
        # 获取昨收价（前一条数据的收盘价）
        if len(df) > 1:
            prev_close = float(df.iloc[-2]['收盘'])
        else:
            prev_close = current_price
        
        # 计算涨跌幅
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        return {
            "price": current_price,
            "prev_close": prev_close,
            "change_pct": change_pct
        }
    except Exception as e:
        print(f"获取 {code} 价格失败：{e}")
        return None

def check_alert(stock, price_info):
    """检查是否触发预警"""
    current_price = price_info["price"]
    change_pct = price_info["change_pct"]
    cost = stock["cost"]
    
    # 计算相对于成本的涨跌幅
    cost_change_pct = ((current_price - cost) / cost) * 100
    
    # 检查预警阈值（按日涨跌幅）
    for threshold in sorted(THRESHOLDS, key=lambda x: abs(x["pct"]), reverse=True):
        if threshold["type"] == "gain" and change_pct >= threshold["pct"]:
            return {
                "triggered": True,
                "message": threshold["message"],
                "change_pct": change_pct,
                "cost_change_pct": cost_change_pct
            }
        elif threshold["type"] == "loss" and change_pct <= threshold["pct"]:
            return {
                "triggered": True,
                "message": threshold["message"],
                "change_pct": change_pct,
                "cost_change_pct": cost_change_pct
            }
    
    return {"triggered": False}

def main():
    """主函数"""
    alerts = []
    
    for stock in HOLDINGS:
        print(f"检查 {stock['name']} ({stock['code']})...")
        price_info = get_stock_price(stock["code"])
        
        if price_info is None:
            print(f"  ⚠️ 无法获取价格数据")
            continue
        
        current_price = price_info["price"]
        change_pct = price_info["change_pct"]
        cost = stock["cost"]
        cost_change_pct = ((current_price - cost) / cost) * 100
        
        print(f"  现价：{current_price:.2f}元")
        print(f"  涨跌：{change_pct:+.2f}%")
        print(f"  成本：{cost:.2f}元")
        print(f"  成本盈亏：{cost_change_pct:+.2f}%")
        
        alert = check_alert(stock, price_info)
        
        if alert["triggered"]:
            print(f"  🔔 触发预警：{alert['message']}")
            alerts.append({
                "stock": stock,
                "price_info": price_info,
                "alert": alert
            })
        else:
            print(f"  ✓ 无预警")
        print()
    
    # 输出结果（供调用方解析）
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alerts": alerts
    }
    
    print("=== JSON OUTPUT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return alerts

if __name__ == "__main__":
    alerts = main()
    exit(0 if len(alerts) == 0 else 1)
