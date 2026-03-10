#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股市场分析报告 - 数据收集脚本
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json

print("=" * 80)
print("A 股市场分析报告")
print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============ 1. 大盘概览 ============
print("\n【1. 大盘概览】")
print("-" * 80)

# 获取主要指数实时行情
try:
    # 上证指数
    sh_index = ak.stock_zh_index_spot(symbol="sh000001")
    print(f"上证指数：{sh_index['最新价'].values[0]:.2f} 点")
    print(f"  涨跌幅：{sh_index['涨跌幅'].values[0]:.2f}%")
    print(f"  成交量：{sh_index['成交量'].values[0]:,} 手")
    
    # 深证成指
    sz_index = ak.stock_zh_index_spot(symbol="sz399001")
    print(f"\n深证成指：{sz_index['最新价'].values[0]:.2f} 点")
    print(f"  涨跌幅：{sz_index['涨跌幅'].values[0]:.2f}%")
    print(f"  成交量：{sz_index['成交量'].values[0]:,} 手")
    
    # 创业板指
    cy_index = ak.stock_zh_index_spot(symbol="sz399006")
    print(f"\n创业板指：{cy_index['最新价'].values[0]:.2f} 点")
    print(f"  涨跌幅：{cy_index['涨跌幅'].values[0]:.2f}%")
    print(f"  成交量：{cy_index['成交量'].values[0]:,} 手")
except Exception as e:
    print(f"获取指数数据失败：{e}")

# ============ 2. 板块分析 ============
print("\n【2. 板块分析】")
print("-" * 80)

try:
    # 获取行业板块行情
    sector_df = ak.stock_board_industry_name_em()
    print(f"行业板块数量：{len(sector_df)}")
    
    # 按涨跌幅排序
    sector_sorted = sector_df.sort_values('涨跌幅', ascending=False)
    
    print("\n📈 本周表现最好的 5 个行业板块：")
    for i, row in sector_sorted.head(5).iterrows():
        print(f"  {row['板块名称']}: {row['涨跌幅']:.2f}% (领涨股：{row.get('领涨股', 'N/A')})")
    
    print("\n📉 本周表现最差的 5 个行业板块：")
    for i, row in sector_sorted.tail(5).iterrows():
        print(f"  {row['板块名称']}: {row['涨跌幅']:.2f}% (领跌股：{row.get('领跌股', 'N/A')})")
except Exception as e:
    print(f"获取板块数据失败：{e}")

# ============ 3. 资金流向 ============
print("\n【3. 资金流向】")
print("-" * 80)

try:
    # 北向资金
    north_flow = ak.stock_hsgt_north_net_flow_in_em(symbol="北向资金")
    print("北向资金流向：")
    print(north_flow.head(10).to_string())
    
    # 主力资金流向
    main_flow = ak.stock_main_force_net_flow_em()
    print("\n主力资金流向（前 10）：")
    print(main_flow.head(10).to_string())
except Exception as e:
    print(f"获取资金流向数据失败：{e}")

# ============ 4. 热门股票分析 ============
print("\n【4. 热门股票深度分析】")
print("-" * 80)

# 选择几只热门股票进行分析
hot_stocks = [
    "600519",  # 贵州茅台
    "000858",  # 五粮液
    "300750",  # 宁德时代
    "601318",  # 中国平安
    "000333",  # 美的集团
]

for stock_code in hot_stocks:
    try:
        print(f"\n{'='*60}")
        print(f"股票：{stock_code}")
        
        # 获取实时行情
        stock_spot = ak.stock_zh_a_spot_em()
        stock_info = stock_spot[stock_spot['代码'] == stock_code]
        
        if len(stock_info) > 0:
            row = stock_info.iloc[0]
            print(f"  最新价：{row['最新价']}")
            print(f"  涨跌幅：{row['涨跌幅']}%")
            print(f"  成交量：{row['成交量']:,}")
            print(f"  成交额：{row['成交额']:,}")
        
        # 获取基本面数据
        try:
            stock_profile = ak.stock_profile_em(symbol=stock_code)
            print(f"  市盈率 (PE): {stock_profile['市盈率'].values[0] if len(stock_profile) > 0 else 'N/A'}")
            print(f"  市净率 (PB): {stock_profile['市净率'].values[0] if len(stock_profile) > 0 else 'N/A'}")
        except:
            print("  基本面数据暂缺")
            
    except Exception as e:
        print(f"  获取股票 {stock_code} 数据失败：{e}")

# ============ 5. 市场情绪 ============
print("\n【5. 市场情绪】")
print("-" * 80)

try:
    # 涨停跌停统计
    limit_up = ak.stock_zt_pool_em(date=datetime.now().strftime('%Y%m%d'))
    limit_down = ak.stock_dt_pool_em(date=datetime.now().strftime('%Y%m%d'))
    
    print(f"涨停家数：{len(limit_up)}")
    print(f"跌停家数：{len(limit_down)}")
    print(f"涨跌比：{len(limit_up) / max(len(limit_down), 1):.2f}")
    
    # 市场热度
    if len(limit_up) > 50:
        print("市场情绪：🔥 火热")
    elif len(limit_up) > 20:
        print("市场情绪：😊 乐观")
    elif len(limit_up) > 5:
        print("市场情绪：😐 中性")
    else:
        print("市场情绪：😟 低迷")
        
except Exception as e:
    print(f"获取市场情绪数据失败：{e}")

print("\n" + "=" * 80)
print("报告生成完成")
print("=" * 80)
