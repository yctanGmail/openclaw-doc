#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石油板块深度分析报告
数据来源：akshare
分析时间：2026-03-09
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("石油板块深度分析报告")
print("数据获取时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

# ==================== 1. 石油板块指数分析 ====================
print("\n" + "=" * 80)
print("一、石油板块现状分析")
print("=" * 80)

# 获取石油板块指数数据
try:
    # 石油板块指数 (使用行业指数)
    oil_index_df = ak.stock_board_industry_hist_em(symbol="石油石化", period="daily", start_date="20251209", end_date="20260309")
    
    if len(oil_index_df) > 0:
        print("\n【石油板块指数走势】")
        print(f"数据区间：{oil_index_df['交易日'].min()} 至 {oil_index_df['交易日'].max()}")
        
        # 计算不同周期涨跌幅
        latest_close = oil_index_df['收盘'].iloc[-1]
        
        # 1 周前
        one_week_ago = oil_index_df[oil_index_df['交易日'] <= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')]
        if len(one_week_ago) > 0:
            week_ago_close = one_week_ago['收盘'].iloc[-1]
            week_change = ((latest_close - week_ago_close) / week_ago_close) * 100
            print(f"1 周涨跌幅：{week_change:+.2f}%")
        
        # 1 个月前
        one_month_ago = oil_index_df[oil_index_df['交易日'] <= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')]
        if len(one_month_ago) > 0:
            month_ago_close = one_month_ago['收盘'].iloc[-1]
            month_change = ((latest_close - month_ago_close) / month_ago_close) * 100
            print(f"1 个月涨跌幅：{month_change:+.2f}%")
        
        # 3 个月前
        three_months_ago = oil_index_df[oil_index_df['交易日'] <= (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')]
        if len(three_months_ago) > 0:
            three_month_ago_close = three_months_ago['收盘'].iloc[-1]
            three_month_change = ((latest_close - three_month_ago_close) / three_month_ago_close) * 100
            print(f"3 个月涨跌幅：{three_month_change:+.2f}%")
        
        print(f"\n当前指数点位：{latest_close:.2f}")
except Exception as e:
    print(f"获取板块指数数据失败：{e}")
    print("尝试使用替代数据源...")

# 获取大盘对比数据 (上证指数)
try:
    sh_index_df = ak.stock_zh_index_daily(symbol="sh000001")
    sh_index_df['trade_date'] = sh_index_df['date'].astype(str)
    
    # 筛选最近 3 个月数据
    sh_index_df = sh_index_df[sh_index_df['trade_date'] >= '20251209']
    
    if len(sh_index_df) > 0:
        print("\n【上证指数对比】")
        sh_latest = sh_index_df['close'].iloc[-1]
        
        sh_one_week = sh_index_df[sh_index_df['trade_date'] <= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')]
        if len(sh_one_week) > 0:
            sh_week_change = ((sh_latest - sh_one_week['close'].iloc[-1]) / sh_one_week['close'].iloc[-1]) * 100
            print(f"上证指数 1 周涨跌幅：{sh_week_change:+.2f}%")
        
        sh_one_month = sh_index_df[sh_index_df['trade_date'] <= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')]
        if len(sh_one_month) > 0:
            sh_month_change = ((sh_latest - sh_one_month['close'].iloc[-1]) / sh_one_month['close'].iloc[-1]) * 100
            print(f"上证指数 1 个月涨跌幅：{sh_month_change:+.2f}%")
        
        sh_three_months = sh_index_df[sh_index_df['trade_date'] <= (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')]
        if len(sh_three_months) > 0:
            sh_three_month_change = ((sh_latest - sh_three_months['close'].iloc[-1]) / sh_three_months['close'].iloc[-1]) * 100
            print(f"上证指数 3 个月涨跌幅：{sh_three_month_change:+.2f}%")
except Exception as e:
    print(f"获取上证指数数据失败：{e}")

# ==================== 2. 主要石油股票分析 ====================
print("\n" + "=" * 80)
print("二、主要石油股票对比分析")
print("=" * 80)

oil_stocks = {
    '601857': '中国石油',
    '600028': '中国石化',
    '601808': '中海油服',
    '600871': '石化油服'
}

stock_data = {}

for code, name in oil_stocks.items():
    print(f"\n【{name} ({code})】")
    try:
        # 获取实时行情
        stock_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20251209", end_date="20260309")
        
        if len(stock_df) > 0:
            current_price = stock_df['收盘'].iloc[-1]
            print(f"  当前股价：{current_price:.2f} 元")
            
            # 计算涨跌幅
            if len(stock_df) > 5:
                week_ago = stock_df[stock_df['日期'] <= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')]
                if len(week_ago) > 0:
                    week_change = ((current_price - week_ago['收盘'].iloc[-1]) / week_ago['收盘'].iloc[-1]) * 100
                    print(f"  1 周涨跌幅：{week_change:+.2f}%")
            
            if len(stock_df) > 20:
                month_ago = stock_df[stock_df['日期'] <= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')]
                if len(month_ago) > 0:
                    month_change = ((current_price - month_ago['收盘'].iloc[-1]) / month_ago['收盘'].iloc[-1]) * 100
                    print(f"  1 个月涨跌幅：{month_change:+.2f}%")
            
            # 获取估值数据
            try:
                stock_info = ak.stock_profile_em(symbol=code)
                # 获取市盈率、市净率等
                pe_ratio = stock_info['市盈率 - 动态'].iloc[0] if '市盈率 - 动态' in stock_info.columns else 'N/A'
                pb_ratio = stock_info['市净率'].iloc[0] if '市净率' in stock_info.columns else 'N/A'
                print(f"  市盈率 (PE): {pe_ratio}")
                print(f"  市净率 (PB): {pb_ratio}")
            except:
                print(f"  估值数据获取失败")
            
            # 获取股息率
            try:
                dividend_df = ak.stock_dividend_cn(symbol=code)
                if len(dividend_df) > 0:
                    latest_dividend = dividend_df.iloc[0]
                    print(f"  最近分红：{latest_dividend.get('每股分红', 'N/A')}")
            except:
                pass
            
            stock_data[code] = {
                'name': name,
                'price': current_price,
                'affordable': current_price < 50
            }
            
    except Exception as e:
        print(f"  数据获取失败：{e}")

# ==================== 3. 国际油价分析 ====================
print("\n" + "=" * 80)
print("三、国际油价走势")
print("=" * 80)

try:
    # 获取原油期货数据
    oil_futures_df = ak.futures_hist_em(symbol="原油", period="daily", start_date="20251209", end_date="20260309")
    
    if len(oil_futures_df) > 0:
        print("\n【原油期货走势】")
        print(f"数据区间：{oil_futures_df['日期'].min()} 至 {oil_futures_df['日期'].max()}")
        
        latest_oil = oil_futures_df['收盘'].iloc[-1]
        print(f"最新油价：{latest_oil:.2f}")
        
        # 计算涨跌幅
        week_ago_oil = oil_futures_df[oil_futures_df['日期'] <= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')]
        if len(week_ago_oil) > 0:
            oil_week_change = ((latest_oil - week_ago_oil['收盘'].iloc[-1]) / week_ago_oil['收盘'].iloc[-1]) * 100
            print(f"1 周涨跌幅：{oil_week_change:+.2f}%")
        
        month_ago_oil = oil_futures_df[oil_futures_df['日期'] <= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')]
        if len(month_ago_oil) > 0:
            oil_month_change = ((latest_oil - month_ago_oil['收盘'].iloc[-1]) / month_ago_oil['收盘'].iloc[-1]) * 100
            print(f"1 个月涨跌幅：{oil_month_change:+.2f}%")
            
except Exception as e:
    print(f"获取油价数据失败：{e}")
    print("尝试获取布伦特原油数据...")
    try:
        brent_df = ak.futures_brent_index()
        if len(brent_df) > 0:
            print(f"布伦特原油指数：{brent_df['最新价'].iloc[0]}")
    except Exception as e2:
        print(f"布伦特原油数据获取失败：{e2}")

# ==================== 4. 板块估值分析 ====================
print("\n" + "=" * 80)
print("四、石油板块估值水平")
print("=" * 80)

try:
    # 获取行业估值数据
    industry_pe_df = ak.stock_board_industry_cons_em(symbol="石油石化")
    
    if len(industry_pe_df) > 0:
        print("\n【石油石化行业成分股】")
        print(f"成分股数量：{len(industry_pe_df)}")
        
        # 筛选股价<50 元的股票
        affordable_stocks = industry_pe_df[industry_pe_df['最新价'] < 50]
        print(f"股价<50 元的股票：{len(affordable_stocks)}只")
        
        # 显示前 10 只
        print("\n股价<50 元的股票 Top10:")
        print(affordable_stocks[['代码', '名称', '最新价', '市盈率 - 动态', '市净率', '股息率']].head(10).to_string())
        
except Exception as e:
    print(f"获取行业估值数据失败：{e}")

# ==================== 5. 技术面分析 ====================
print("\n" + "=" * 80)
print("五、技术面分析")
print("=" * 80)

for code, name in oil_stocks.items():
    try:
        stock_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20251201", end_date="20260309")
        
        if len(stock_df) > 20:
            print(f"\n【{name} 技术分析】")
            
            # 计算均线
            stock_df['MA5'] = stock_df['收盘'].rolling(5).mean()
            stock_df['MA10'] = stock_df['收盘'].rolling(10).mean()
            stock_df['MA20'] = stock_df['收盘'].rolling(20).mean()
            stock_df['MA60'] = stock_df['收盘'].rolling(60).mean()
            
            current_price = stock_df['收盘'].iloc[-1]
            ma5 = stock_df['MA5'].iloc[-1]
            ma20 = stock_df['MA20'].iloc[-1]
            ma60 = stock_df['MA60'].iloc[-1]
            
            print(f"  当前价格：{current_price:.2f}")
            print(f"  5 日均线：{ma5:.2f} ({'高于' if current_price > ma5 else '低于'}均线)")
            print(f"  20 日均线：{ma20:.2f} ({'高于' if current_price > ma20 else '低于'}均线)")
            print(f"  60 日均线：{ma60:.2f} ({'高于' if current_price > ma60 else '低于'}均线)")
            
            # 计算近期高低点
            recent_high = stock_df['最高'].tail(20).max()
            recent_low = stock_df['最低'].tail(20).min()
            print(f"  20 日最高：{recent_high:.2f} (阻力位)")
            print(f"  20 日最低：{recent_low:.2f} (支撑位)")
            
    except Exception as e:
        print(f"{name} 技术分析失败：{e}")

# ==================== 6. 资金流向分析 ====================
print("\n" + "=" * 80)
print("六、资金流向分析")
print("=" * 80)

for code, name in oil_stocks.items():
    try:
        # 获取资金流向数据
        fund_flow_df = ak.stock_individual_fund_flow(symbol=code, market="sh", indicator="今日")
        
        if len(fund_flow_df) > 0:
            print(f"\n【{name} 资金流向】")
            print(fund_flow_df.to_string())
            
    except Exception as e:
        print(f"{name} 资金流向数据获取失败：{e}")

# ==================== 7. 综合分析与建议 ====================
print("\n" + "=" * 80)
print("七、投资建议")
print("=" * 80)

print("""
【综合分析】

1. 板块走势判断:
   - 石油板块近期受国际油价波动影响较大
   - 需关注 OPEC+ 政策变化及地缘政治局势
   - 国内能源安全政策提供长期支撑

2. 估值水平:
   - 石油板块整体估值处于历史中低位
   - 央企国企改革预期提供估值修复动力

3. 风险提示:
   - 国际油价波动风险
   - 新能源替代长期压力
   - 地缘政治不确定性

【操作建议】

基于谭老师的情况 (1.2 万预算，新手，风险承受 -20%):

1. 仓位建议：建议首次建仓不超过总预算的 50% (6000 元)
2. 选股建议：优先选择低估值、高股息的央企龙头
3. 买入策略：分批建仓，避免一次性买入
4. 止损设置：建议设置 -10% 止损线
5. 目标价位：建议 15-20% 收益目标

【具体推荐】

请根据上述数据分析结果，选择:
- 股价<10 元的股票更适合新手 (可买更多股数，心理压力小)
- 优先选择 PE<10, PB<1 的低估值股票
- 关注股息率>3% 的股票提供安全垫

【明日操作】

如果明天开盘:
- 板块指数高开<1%: 可考虑小幅建仓
- 板块指数高开>2%: 建议等待回调
- 板块指数低开: 观察支撑位，可逢低吸纳

免责声明：以上分析仅供参考，不构成投资建议。
投资有风险，入市需谨慎。
""")

print("\n" + "=" * 80)
print("报告生成完毕")
print("=" * 80)
