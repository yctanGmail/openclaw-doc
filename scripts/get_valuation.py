#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取石油股估值数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

print("获取石油股估值数据...")
print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

stocks = ['601857', '600028', '601808', '600871']
names = {'601857': '中国石油', '600028': '中国石化', '601808': '中海油服', '600871': '石化油服'}

results = []

for code in stocks:
    print(f"\n正在获取 {names[code]} ({code}) 数据...")
    
    try:
        # 方法 1: 获取个股实时行情
        stock_df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq", start_date="20260301", end_date="20260309")
        
        if len(stock_df) > 0:
            current_price = stock_df['收盘'].iloc[-1]
            print(f"  当前价格：{current_price:.2f}")
            
            # 获取估值指标
            try:
                # 尝试获取 F10 资料
                stock_info = ak.stock_individual_info_em(symbol=code)
                print(f"  股票信息获取成功，共{len(stock_info)}项")
                
                # 提取关键指标
                pe = None
                pb = None
                dividend = None
                
                for _, row in stock_info.iterrows():
                    item = row['item']
                    value = row['value']
                    
                    if '市盈率' in str(item):
                        try:
                            pe = float(str(value).replace('倍', '').strip())
                        except:
                            pass
                    if '市净率' in str(item):
                        try:
                            pb = float(str(value).replace('倍', '').strip())
                        except:
                            pass
                    if '股息' in str(item) or '分红' in str(item):
                        dividend = value
                
                print(f"  PE: {pe}, PB: {pb}, 股息：{dividend}")
                
            except Exception as e:
                print(f"  F10 获取失败：{e}")
                
        else:
            print(f"  无历史数据")
            
    except Exception as e:
        print(f"  获取失败：{e}")
    
    time.sleep(1)

# 尝试获取行业板块数据
print("\n" + "=" * 80)
print("获取石油板块整体数据...")

try:
    # 获取石油板块成分股
    sector_df = ak.stock_board_industry_cons_em(symbol="石油石化")
    
    if len(sector_df) > 0:
        print(f"\n石油石化板块共{len(sector_df)}只成分股")
        print("\n主要成分股:")
        print(sector_df[['代码', '名称', '最新价', '涨跌幅', '市盈率 - 动态', '市净率', '股息率']].to_string())
        
except Exception as e:
    print(f"板块数据获取失败：{e}")

# 获取国际油价
print("\n" + "=" * 80)
print("获取国际油价数据...")

try:
    # WTI 原油
    wt_df = ak.futures_hist_em(symbol="原油", period="daily", start_date="20260201", end_date="20260309")
    if len(wt_df) > 0:
        print(f"\nWTI 原油最新：{wt_df['收盘'].iloc[-1]}美元")
except Exception as e:
    print(f"WTI 获取失败：{e}")

try:
    # 布伦特原油
    br_df = ak.futures_brent_daily()
    if len(br_df) > 0:
        print(f"布伦特原油最新：{br_df['最新价'].iloc[0]}美元")
except Exception as e:
    print(f"布伦特获取失败：{e}")

print("\n" + "=" * 80)
print("数据获取完成")
