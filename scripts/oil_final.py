#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石油板块分析报告 - 最终版
使用多种数据源获取数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("石油板块深度分析报告")
print("生成时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

# 股票列表
stocks = {
    '601857': '中国石油',
    '600028': '中国石化', 
    '601808': '中海油服',
    '600871': '石化油服'
}

results = {}

print("\n" + "=" * 80)
print("一、股票数据获取")
print("=" * 80)

for code, name in stocks.items():
    print(f"\n【{name} ({code})】")
    results[code] = {'name': name, 'code': code}
    
    # 尝试多种数据源
    try:
        # 方法 1: 获取历史行情 (之前成功过)
        hist_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20251201", end_date="20260309")
        
        if len(hist_df) > 0:
            current_price = hist_df['收盘'].iloc[-1]
            results[code]['price'] = current_price
            print(f"  ✓ 当前股价：{current_price:.2f}元")
            
            # 计算涨跌幅
            hist_df['日期'] = pd.to_datetime(hist_df['日期'])
            
            # 1 周
            week_ago = hist_df[hist_df['日期'] <= datetime.now() - timedelta(days=7)]
            if len(week_ago) > 0:
                week_change = ((current_price - week_ago['收盘'].iloc[-1]) / week_ago['收盘'].iloc[-1]) * 100
                results[code]['week_change'] = week_change
                print(f"  ✓ 1 周涨跌：{week_change:+.2f}%")
            
            # 1 月
            month_ago = hist_df[hist_df['日期'] <= datetime.now() - timedelta(days=30)]
            if len(month_ago) > 0:
                month_change = ((current_price - month_ago['收盘'].iloc[-1]) / month_ago['收盘'].iloc[-1]) * 100
                results[code]['month_change'] = month_change
                print(f"  ✓ 1 月涨跌：{month_change:+.2f}%")
            
            # 3 月
            three_month_ago = hist_df[hist_df['日期'] <= datetime.now() - timedelta(days=90)]
            if len(three_month_ago) > 0:
                three_month_change = ((current_price - three_month_ago['收盘'].iloc[-1]) / three_month_ago['收盘'].iloc[-1]) * 100
                results[code]['three_month_change'] = three_month_change
                print(f"  ✓ 3 月涨跌：{three_month_change:+.2f}%")
            
            # 60 日高低点
            recent_60 = hist_df.tail(60)
            high_60 = recent_60['最高'].max()
            low_60 = recent_60['最低'].min()
            results[code]['high_60'] = high_60
            results[code]['low_60'] = low_60
            print(f"  ✓ 60 日区间：{low_60:.2f} - {high_60:.2f}元")
            
            # 当前位置
            position = (current_price - low_60) / (high_60 - low_60) * 100
            results[code]['position'] = position
            print(f"  ✓ 当前位置：{position:.1f}% 分位")
            
        else:
            print(f"  ✗ 无历史数据")
            
    except Exception as e:
        print(f"  ✗ 数据获取失败：{str(e)[:100]}")
    
    time.sleep(0.5)

# 获取估值数据 (使用 stock_individual_info_em)
print("\n" + "=" * 80)
print("二、估值指标获取")
print("=" * 80)

for code, name in stocks.items():
    print(f"\n【{name}】")
    try:
        info_df = ak.stock_individual_info_em(symbol=code)
        
        pe = None
        pb = None
        dividend_yield = None
        total_shares = None
        market_cap = None
        
        for _, row in info_df.iterrows():
            item = str(row['item'])
            value = str(row['value'])
            
            if '市盈率' in item:
                try:
                    pe = float(value.replace('倍', '').strip())
                except:
                    pass
            if '市净率' in item:
                try:
                    pb = float(value.replace('倍', '').strip())
                except:
                    pass
            if '总市值' in item:
                try:
                    market_cap = float(value.replace('亿', '').strip()) * 100000000
                except:
                    pass
            if '总股本' in item:
                try:
                    total_shares = float(value.replace('亿股', '').strip()) * 100000000
                except:
                    pass
            if '股息率' in item:
                try:
                    dividend_yield = float(value.replace('%', '').strip())
                except:
                    pass
        
        if pe:
            results[code]['pe'] = pe
            print(f"  ✓ PE: {pe:.2f}")
        if pb:
            results[code]['pb'] = pb
            print(f"  ✓ PB: {pb:.2f}")
        if dividend_yield:
            results[code]['dividend_yield'] = dividend_yield
            print(f"  ✓ 股息率：{dividend_yield:.2f}%")
        if market_cap:
            results[code]['market_cap'] = market_cap
            print(f"  ✓ 市值：{market_cap/100000000:.2f}亿")
            
    except Exception as e:
        print(f"  ✗ 估值获取失败：{str(e)[:100]}")
    
    time.sleep(0.5)

# 上证指数对比
print("\n" + "=" * 80)
print("三、大盘对比")
print("=" * 80)

try:
    sh_df = ak.stock_zh_index_daily(symbol="sh000001")
    sh_df['date'] = pd.to_datetime(sh_df['date'])
    sh_df = sh_df.sort_values('date')
    
    sh_recent = sh_df[sh_df['date'] >= datetime.now() - timedelta(days=90)]
    
    if len(sh_recent) > 0:
        sh_current = sh_recent['close'].iloc[-1]
        print(f"\n上证指数：{sh_current:.2f}")
        
        sh_week = sh_recent[sh_recent['date'] <= datetime.now() - timedelta(days=7)]
        if len(sh_week) > 0:
            sh_week_change = ((sh_current - sh_week['close'].iloc[-1]) / sh_week['close'].iloc[-1]) * 100
            print(f"1 周涨跌：{sh_week_change:+.2f}%")
        
        sh_month = sh_recent[sh_recent['date'] <= datetime.now() - timedelta(days=30)]
        if len(sh_month) > 0:
            sh_month_change = ((sh_current - sh_month['close'].iloc[-1]) / sh_month['close'].iloc[-1]) * 100
            print(f"1 月涨跌：{sh_month_change:+.2f}%")
            
        results['sh_index'] = {
            'current': sh_current,
            'week_change': sh_week_change if len(sh_week) > 0 else None,
            'month_change': sh_month_change if len(sh_month) > 0 else None
        }
        
except Exception as e:
    print(f"上证指数获取失败：{e}")

# 国际油价
print("\n" + "=" * 80)
print("四、国际油价")
print("=" * 80)

# 尝试获取油价数据
oil_sources = [
    ('原油', 'futures_hist_em'),
    ('CL00', 'futures_zh_daily_sina'),
]

for symbol, func_name in oil_sources:
    try:
        if func_name == 'futures_hist_em':
            oil_df = ak.futures_hist_em(symbol=symbol, period="daily", start_date="20260201", end_date="20260309")
        elif func_name == 'futures_zh_daily_sina':
            oil_df = ak.futures_zh_daily_sina(symbol=symbol)
        
        if len(oil_df) > 0:
            print(f"\n✓ {symbol}: {oil_df['收盘'].iloc[-1] if '收盘' in oil_df.columns else oil_df['close'].iloc[-1]}")
            break
    except Exception as e:
        continue

# 汇总表格
print("\n" + "=" * 80)
print("五、数据汇总")
print("=" * 80)

print("\n| 股票 | 股价 | PE | PB | 股息率 | 1 周 | 1 月 | 3 月 | 60 日位置 |")
print("|------|------|----|----|--------|------|------|------|----------|")

for code, data in results.items():
    if code == 'sh_index':
        continue
    
    price = f"{data.get('price', 0):.2f}" if 'price' in data else "N/A"
    pe = f"{data.get('pe', 0):.1f}" if 'pe' in data else "N/A"
    pb = f"{data.get('pb', 0):.1f}" if 'pb' in data else "N/A"
    div = f"{data.get('dividend_yield', 0):.1f}%" if 'dividend_yield' in data else "N/A"
    week = f"{data.get('week_change', 0):+.1f}%" if 'week_change' in data else "N/A"
    month = f"{data.get('month_change', 0):+.1f}%" if 'month_change' in data else "N/A"
    three = f"{data.get('three_month_change', 0):+.1f}%" if 'three_month_change' in data else "N/A"
    pos = f"{data.get('position', 0):.0f}%" if 'position' in data else "N/A"
    
    print(f"| {data['name']} | {price} | {pe} | {pb} | {div} | {week} | {month} | {three} | {pos} |")

# 投资建议
print("\n" + "=" * 80)
print("六、投资建议")
print("=" * 80)

# 计算综合评分
for code, data in results.items():
    if code == 'sh_index':
        continue
    
    score = 0
    reasons = []
    
    # 低估值加分
    if data.get('pe', 999) < 10:
        score += 30
        reasons.append("低 PE")
    elif data.get('pe', 999) < 15:
        score += 20
        reasons.append("合理 PE")
    
    # 低 PB 加分
    if data.get('pb', 999) < 1:
        score += 25
        reasons.append("低 PB")
    elif data.get('pb', 999) < 1.5:
        score += 15
        reasons.append("合理 PB")
    
    # 高股息加分
    if data.get('dividend_yield', 0) > 4:
        score += 20
        reasons.append("高股息")
    elif data.get('dividend_yield', 0) > 3:
        score += 10
        reasons.append("股息尚可")
    
    # 股价低适合新手
    if data.get('price', 999) < 10:
        score += 10
        reasons.append("低价股")
    
    # 位置低加分
    if data.get('position', 100) < 50:
        score += 10
        reasons.append("位置较低")
    
    data['score'] = score
    data['reasons'] = reasons

# 找出最佳选择
best_code = None
best_score = -1

for code, data in results.items():
    if code == 'sh_index':
        continue
    if data.get('score', 0) > best_score:
        best_score = data['score']
        best_code = code

if best_code:
    best = results[best_code]
    print(f"""
【综合推荐】{best['name']} ({best_code})
综合评分：{best_score}分
推荐理由：{', '.join(best.get('reasons', []))}

关键数据:
- 当前股价：{best.get('price', 'N/A')}元
- PE: {best.get('pe', 'N/A')}
- PB: {best.get('pb', 'N/A')}
- 股息率：{best.get('dividend_yield', 'N/A')}%
- 60 日位置：{best.get('position', 'N/A')}%

【操作建议】

基于谭老师情况：
- 总投资：1.2 万元
- 风险承受：-20%
- 投资期限：1-3 年
- 经验：新手

1. 仓位建议:
   - 首笔：5000-6000 元 (50% 仓位)
   - 剩余：等待回调或定投

2. 买入策略:
   - 理想价格：{best.get('price', 0) * 0.98:.2f} - {best.get('price', 0) * 1.02:.2f}元
   - 如果高开>2%：等待回调
   - 如果平开或低开：可建仓

3. 止损设置:
   - 止损位：{best.get('price', 0) * 0.9:.2f}元 (-10%)
   - 最大亏损：约 500-600 元

4. 目标价位:
   - 第一目标：{best.get('price', 0) * 1.15:.2f}元 (+15%)
   - 第二目标：{best.get('price', 0) * 1.2:.2f}元 (+20%)

5. 持有策略:
   - 长期持有 1-3 年
   - 收取股息
   - 季度复盘

【备选股票】
""")

    # 显示备选
    for code, data in results.items():
        if code != best_code and code != 'sh_index' and data.get('price', 0) < 20:
            print(f"- {data['name']} ({code}): {data.get('price', 0):.2f}元，PE={data.get('pe', 'N/A')}, 股息率={data.get('dividend_yield', 'N/A')}%")

print("""
【风险提示】
⚠️ 国际油价波动
⚠️ 新能源替代压力
⚠️ 地缘政治风险
⚠️ 股市有风险，投资需谨慎

【免责声明】
以上分析基于公开数据，仅供参考，不构成投资建议。
""")

print("\n" + "=" * 80)
print("报告完成")
print("=" * 80)
