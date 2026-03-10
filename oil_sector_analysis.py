#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石油板块分析报告
数据来源：akshare
分析时间：2026-03-09
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import json

print("=" * 60)
print("石油板块分析报告")
print("数据获取时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 60)

# ============ 1. 获取石油板块指数数据 ============
print("\n【1. 石油板块指数】")
try:
    # 获取石油板块指数 (使用行业板块)
    #  akshare 的指数数据
    stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
    print("可用的行业板块:")
    oil_related = stock_board_industry_name_em_df[stock_board_industry_name_em_df['板块名称'].str.contains('油|石油|石化', na=False)]
    print(oil_related[['板块名称', '板块代码']].to_string())
except Exception as e:
    print(f"获取板块指数失败：{e}")

# ============ 2. 获取石油个股实时行情 ============
print("\n【2. 石油个股实时行情】")
oil_stocks = {
    '601857': '中国石油',
    '600028': '中国石化', 
    '601808': '中海油服',
    '600871': '石化油服'
}

stock_data = {}
for code, name in oil_stocks.items():
    try:
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        stock_info = df[df['代码'] == code]
        if not stock_info.empty:
            stock_data[code] = {
                'name': name,
                'price': stock_info['最新价'].values[0],
                'change_pct': stock_info['涨跌幅'].values[0],
                'pe': stock_info['市盈率-动态'].values[0],
                'pb': stock_info['市净率'].values[0],
                'market_cap': stock_info['总市值'].values[0],
                'volume': stock_info['成交量'].values[0]
            }
            print(f"{code} {name}: 股价={stock_data[code]['price']}, 涨跌幅={stock_data[code]['change_pct']}%, PE={stock_data[code]['pe']}, PB={stock_data[code]['pb']}")
    except Exception as e:
        print(f"获取 {code} 数据失败：{e}")

# ============ 3. 获取个股详细财务数据 ============
print("\n【3. 个股详细财务指标】")
for code, name in oil_stocks.items():
    try:
        # 获取财务指标
        df = ak.stock_financial_analysis_indicator(symbol=code, start_year="2023")
        if not df.empty:
            latest = df.iloc[-1]
            print(f"\n{code} {name} 最新财务指标:")
            print(f"  每股收益：{latest.get('每股收益', 'N/A')}")
            print(f"  净资产收益率：{latest.get('净资产收益率', 'N/A')}")
            print(f"  销售净利率：{latest.get('销售净利率', 'N/A')}")
    except Exception as e:
        print(f"获取 {code} 财务指标失败：{e}")

# ============ 4. 获取股息率数据 ============
print("\n【4. 股息率数据】")
for code, name in oil_stocks.items():
    try:
        # 获取分红数据
        df = ak.stock_dividend(symbol=code)
        if not df.empty:
            latest_dividend = df.iloc[0] if len(df) > 0 else None
            if latest_dividend is not None:
                dividend_amount = latest_dividend.get('每股分红', 0)
                if code in stock_data and stock_data[code]['price'] > 0:
                    dividend_yield = (dividend_amount / stock_data[code]['price']) * 100
                    print(f"{code} {name}: 每股分红={dividend_amount}元，股息率≈{dividend_yield:.2f}%")
    except Exception as e:
        print(f"获取 {code} 分红数据失败：{e}")

# ============ 5. 获取国际油价数据 ============
print("\n【5. 国际油价】")
try:
    # 获取原油期货数据
    oil_futures_df = ak.futures_display_main_sina()
    oil_futures = oil_futures_df[oil_futures_df['symbol'].str.contains('原油|WTI|布伦特', na=False)]
    print("原油期货:")
    print(oil_futures[['symbol', 'last_close', 'open', 'high', 'low']].to_string())
except Exception as e:
    print(f"获取原油期货数据失败：{e}")

# ============ 6. 获取板块 K 线数据 ============
print("\n【6. 板块走势分析】")
try:
    # 尝试获取行业板块 K 线
    # 使用东方财富行业板块指数
    for code, name in oil_stocks.items():
        try:
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20251209", end_date="20260309")
            if not df.empty:
                recent = df.tail(5)
                print(f"\n{code} {name} 近 5 日走势:")
                print(recent[['日期', '收盘', '成交量']].to_string())
                
                # 计算涨跌幅
                if len(df) > 20:
                    week_change = ((df.iloc[-1]['收盘'] - df.iloc[-5]['收盘']) / df.iloc[-5]['收盘']) * 100
                    month_change = ((df.iloc[-1]['收盘'] - df.iloc[-20]['收盘']) / df.iloc[-20]['收盘']) * 100
                    print(f"  近 1 周涨跌幅：{week_change:.2f}%")
                    print(f"  近 1 月涨跌幅：{month_change:.2f}%")
        except Exception as e:
            print(f"获取 {code} K 线失败：{e}")
except Exception as e:
    print(f"获取 K 线数据失败：{e}")

# ============ 7. 获取资金流向 ============
print("\n【7. 资金流向】")
for code, name in oil_stocks.items():
    try:
        df = ak.stock_individual_fund_flow_rank(indicator="今日")
        if not df.empty:
            stock_flow = df[df['代码'] == code]
            if not stock_flow.empty:
                print(f"{code} {name}: 主力资金={stock_flow.iloc[0].get('主力净流入-净额', 'N/A')}万")
    except Exception as e:
        print(f"获取 {code} 资金流向失败：{e}")

print("\n" + "=" * 60)
print("数据获取完成")
print("=" * 60)
