#!/usr/bin/env python3
"""
持仓股票价格预警监控
检查频率：每 15 分钟（交易时间内）
"""

import akshare as ak
import json
from datetime import datetime

# 持仓配置
HOLDINGS = [
    {"name": "招商银行", "code": "600036", "cost": 38.90},
    {"name": "紫金矿业", "code": "601899", "cost": 35.12},
]

# 预警阈值
THRESHOLDS = [
    {"pct": 7, "msg": "建议减仓"},
    {"pct": 5, "msg": "考虑止盈"},
    {"pct": -8, "msg": "考虑止损"},
    {"pct": -5, "msg": "检查基本面"},
]

def get_stock_price(code):
    """获取股票实时行情"""
    try:
        # 使用 akshare 获取实时行情
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == code]
        if len(stock) > 0:
            return {
                "price": float(stock.iloc[0]['最新价']),
                "change_pct": float(stock.iloc[0]['涨跌幅'])
            }
    except Exception as e:
        print(f"获取 {code} 数据失败：{e}")
    return None

def check_alert(stock_info, holding):
    """检查是否触发预警"""
    current_price = stock_info["price"]
    cost = holding["cost"]
    change_from_cost = ((current_price - cost) / cost) * 100
    
    # 按阈值从高到低检查
    for threshold in sorted(THRESHOLDS, key=lambda x: abs(x["pct"]), reverse=True):
        if threshold["pct"] > 0 and change_from_cost >= threshold["pct"]:
            return {
                "triggered": True,
                "message": threshold["msg"],
                "change_pct": change_from_cost
            }
        elif threshold["pct"] < 0 and change_from_cost <= threshold["pct"]:
            return {
                "triggered": True,
                "message": threshold["msg"],
                "change_pct": change_from_cost
            }
    
    return {"triggered": False, "change_pct": change_from_cost}

def main():
    """主函数"""
    alerts = []
    
    for holding in HOLDINGS:
        stock_info = get_stock_price(holding["code"])
        if not stock_info:
            continue
        
        result = check_alert(stock_info, holding)
        
        if result["triggered"]:
            alert = {
                "name": holding["name"],
                "code": holding["code"],
                "price": stock_info["price"],
                "change_pct": result["change_pct"],
                "message": result["message"]
            }
            alerts.append(alert)
    
    # 输出结果
    if alerts:
        print(json.dumps({"alerts": alerts}, ensure_ascii=False))
    else:
        print(json.dumps({"alerts": []}, ensure_ascii=False))

if __name__ == "__main__":
    main()
