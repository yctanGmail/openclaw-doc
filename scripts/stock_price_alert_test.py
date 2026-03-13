#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票价格预警监控 - 测试版本（忽略交易时间）
"""

import akshare as ak
import json
from datetime import datetime

# 持仓配置
HOLDINGS = [
    {"name": "招商银行", "code": "600036", "cost": 38.90},
    {"name": "紫金矿业", "code": "601899", "cost": 35.12}
]

def main():
    print(f"测试运行 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        stock_data = ak.stock_zh_a_spot_em()
        print(f"获取到 {len(stock_data)} 只股票数据")
        
        for stock in HOLDINGS:
            code = stock["code"]
            stock_info = stock_data[stock_data["代码"] == code]
            
            if len(stock_info) > 0:
                row = stock_info.iloc[0]
                current_price = float(row["最新价"])
                change_pct = float(row["涨跌幅"])
                cost = stock["cost"]
                cost_change_pct = ((current_price - cost) / cost) * 100
                
                print(f"\n{stock['name']} ({code}):")
                print(f"  现价：{current_price:.2f} 元")
                print(f"  今日涨跌：{change_pct:.2f}%")
                print(f"  成本：{cost:.2f} 元")
                print(f"  相对成本涨跌：{cost_change_pct:+.2f}%")
                
                # 检查预警
                if cost_change_pct >= 7:
                    print(f"  ⚠️  触发预警：建议减仓")
                elif cost_change_pct >= 5:
                    print(f"  ⚠️  触发预警：考虑止盈")
                elif cost_change_pct <= -8:
                    print(f"  ⚠️  触发预警：考虑止损")
                elif cost_change_pct <= -5:
                    print(f"  ⚠️  触发预警：检查基本面")
                else:
                    print(f"  ✅ 无预警")
            else:
                print(f"未找到股票 {code} 的数据")
                
    except Exception as e:
        print(f"错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
