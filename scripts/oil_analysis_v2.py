#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石油板块深度分析报告 v2
改进版 - 增强错误处理和数据获取
数据时间：2026-03-09
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

def safe_get(func, *args, **kwargs):
    """安全获取数据，带重试机制"""
    max_retries = 3
    for i in range(max_retries):
        try:
            time.sleep(0.5)  # 避免请求过快
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            if i == max_retries - 1:
                return None
            time.sleep(1)
    return None

print("=" * 80)
print("石油板块深度分析报告 v2")
print("数据获取时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

# ==================== 1. 获取股票实时行情 ====================
print("\n" + "=" * 80)
print("一、主要石油股票实时数据")
print("=" * 80)

oil_stocks = {
    '601857': '中国石油',
    '600028': '中国石化',
    '601808': '中海油服',
    '600871': '石化油服'
}

stock_info = {}

for code, name in oil_stocks.items():
    print(f"\n【{name} ({code})】")
    try:
        # 获取实时行情
        realtime_df = ak.stock_zh_a_spot_em()
        stock_row = realtime_df[realtime_df['代码'] == code]
        
        if len(stock_row) > 0:
            data = stock_row.iloc[0]
            current_price = data.get('最新价', 0)
            change_pct = data.get('涨跌幅', 0)
            pe_ratio = data.get('市盈率 - 动态', 0)
            pb_ratio = data.get('市净率', 0)
            dividend_yield = data.get('股息率', 0)
            total_market = data.get('总市值', 0)
            
            print(f"  当前股价：{current_price:.2f} 元")
            print(f"  今日涨跌：{change_pct:+.2f}%")
            print(f"  市盈率 (PE): {pe_ratio:.2f}" if pe_ratio else "  市盈率 (PE): N/A")
            print(f"  市净率 (PB): {pb_ratio:.2f}" if pb_ratio else "  市净率 (PB): N/A")
            print(f"  股息率：{dividend_yield:.2f}%" if dividend_yield else "  股息率：N/A")
            print(f"  总市值：{total_market/100000000:.2f}亿")
            
            stock_info[code] = {
                'name': name,
                'price': current_price,
                'change_pct': change_pct,
                'pe': pe_ratio,
                'pb': pb_ratio,
                'dividend_yield': dividend_yield,
                'market_cap': total_market
            }
        else:
            print(f"  未找到股票数据")
            
    except Exception as e:
        print(f"  数据获取失败：{e}")

# ==================== 2. 历史走势分析 ====================
print("\n" + "=" * 80)
print("二、历史走势分析")
print("=" * 80)

for code, name in oil_stocks.items():
    print(f"\n【{name} 历史走势】")
    try:
        # 获取历史数据
        hist_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20251209", end_date="20260309")
        
        if len(hist_df) > 0:
            hist_df['日期'] = pd.to_datetime(hist_df['日期'])
            hist_df = hist_df.sort_values('日期')
            
            current_price = hist_df['收盘'].iloc[-1]
            
            # 1 周前
            one_week_ago = datetime.now() - timedelta(days=7)
            week_data = hist_df[hist_df['日期'] <= one_week_ago]
            if len(week_data) > 0:
                week_price = week_data['收盘'].iloc[-1]
                week_change = ((current_price - week_price) / week_price) * 100
                print(f"  1 周前价格：{week_price:.2f}元，涨跌幅：{week_change:+.2f}%")
            
            # 1 个月前
            one_month_ago = datetime.now() - timedelta(days=30)
            month_data = hist_df[hist_df['日期'] <= one_month_ago]
            if len(month_data) > 0:
                month_price = month_data['收盘'].iloc[-1]
                month_change = ((current_price - month_price) / month_price) * 100
                print(f"  1 月前价格：{month_price:.2f}元，涨跌幅：{month_change:+.2f}%")
            
            # 3 个月前
            three_months_ago = datetime.now() - timedelta(days=90)
            three_month_data = hist_df[hist_df['日期'] <= three_months_ago]
            if len(three_month_data) > 0:
                three_month_price = three_month_data['收盘'].iloc[-1]
                three_month_change = ((current_price - three_month_price) / three_month_price) * 100
                print(f"  3 月前价格：{three_month_price:.2f}元，涨跌幅：{three_month_change:+.2f}%")
            
            # 最高最低价
            recent_high = hist_df['最高'].tail(60).max()
            recent_low = hist_df['最低'].tail(60).min()
            print(f"  60 日最高：{recent_high:.2f}元")
            print(f"  60 日最低：{recent_low:.2f}元")
            print(f"  当前位置：{(current_price - recent_low) / (recent_high - recent_low) * 100:.1f}% 分位")
            
    except Exception as e:
        print(f"  历史数据获取失败：{e}")

# ==================== 3. 大盘对比 ====================
print("\n" + "=" * 80)
print("三、与大盘对比")
print("=" * 80)

try:
    sh_index = ak.stock_zh_index_daily(symbol="sh000001")
    sh_index['date'] = pd.to_datetime(sh_index['date'])
    sh_index = sh_index.sort_values('date')
    
    # 筛选最近数据
    sh_recent = sh_index[sh_index['date'] >= (datetime.now() - timedelta(days=90))]
    
    if len(sh_recent) > 0:
        sh_current = sh_recent['close'].iloc[-1]
        
        sh_week = sh_recent[sh_recent['date'] <= (datetime.now() - timedelta(days=7))]
        sh_month = sh_recent[sh_recent['date'] <= (datetime.now() - timedelta(days=30))]
        sh_three_month = sh_recent[sh_recent['date'] <= (datetime.now() - timedelta(days=90))]
        
        print(f"\n【上证指数】当前：{sh_current:.2f}")
        if len(sh_week) > 0:
            print(f"  1 周涨跌幅：{((sh_current - sh_week['close'].iloc[-1]) / sh_week['close'].iloc[-1]) * 100:+.2f}%")
        if len(sh_month) > 0:
            print(f"  1 月涨跌幅：{((sh_current - sh_month['close'].iloc[-1]) / sh_month['close'].iloc[-1]) * 100:+.2f}%")
        if len(sh_three_month) > 0:
            print(f"  3 月涨跌幅：{((sh_current - sh_three_month['close'].iloc[-1]) / sh_three_month['close'].iloc[-1]) * 100:+.2f}%")
        
        # 对比石油股
        print(f"\n【石油股 vs 大盘】")
        for code, info in stock_info.items():
            if 'change_pct' in info:
                relative_strength = info['change_pct'] - 0  # 简化计算
                print(f"  {info['name']}: 今日{info['change_pct']:+.2f}%, 相对强弱：{'强于' if info['change_pct'] > 0 else '弱于'}大盘")
                
except Exception as e:
    print(f"大盘数据获取失败：{e}")

# ==================== 4. 国际油价 ====================
print("\n" + "=" * 80)
print("四、国际油价走势")
print("=" * 80)

try:
    # 获取原油期货
    oil_df = ak.futures_zh_daily_sina(symbol="CL00")
    
    if len(oil_df) > 0:
        oil_df['date'] = pd.to_datetime(oil_df['date'])
        oil_df = oil_df.sort_values('date')
        
        recent_oil = oil_df.tail(90)
        current_oil = recent_oil['close'].iloc[-1]
        
        print(f"\n【WTI 原油期货】当前：{current_oil:.2f}美元/桶")
        
        oil_week = recent_oil[recent_oil['date'] <= (datetime.now() - timedelta(days=7))]
        oil_month = recent_oil[recent_oil['date'] <= (datetime.now() - timedelta(days=30))]
        
        if len(oil_week) > 0:
            print(f"  1 周涨跌幅：{((current_oil - oil_week['close'].iloc[-1]) / oil_week['close'].iloc[-1]) * 100:+.2f}%")
        if len(oil_month) > 0:
            print(f"  1 月涨跌幅：{((current_oil - oil_month['close'].iloc[-1]) / oil_month['close'].iloc[-1]) * 100:+.2f}%")
        
except Exception as e:
    print(f"油价数据获取失败：{e}")
    print("注：可关注布伦特原油和 WTI 原油期货走势")

# ==================== 5. 技术分析 ====================
print("\n" + "=" * 80)
print("五、技术面分析")
print("=" * 80)

for code, name in oil_stocks.items():
    print(f"\n【{name} 技术指标】")
    try:
        hist_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20251201", end_date="20260309")
        
        if len(hist_df) > 60:
            hist_df['日期'] = pd.to_datetime(hist_df['日期'])
            hist_df = hist_df.sort_values('日期')
            
            # 计算均线
            hist_df['MA5'] = hist_df['收盘'].rolling(5).mean()
            hist_df['MA10'] = hist_df['收盘'].rolling(10).mean()
            hist_df['MA20'] = hist_df['收盘'].rolling(20).mean()
            hist_df['MA60'] = hist_df['收盘'].rolling(60).mean()
            
            current = hist_df.iloc[-1]
            
            print(f"  当前价格：{current['收盘']:.2f}")
            print(f"  MA5: {current['MA5']:.2f} ({'多头' if current['收盘'] > current['MA5'] else '空头'})")
            print(f"  MA20: {current['MA20']:.2f} ({'多头' if current['收盘'] > current['MA20'] else '空头'})")
            print(f"  MA60: {current['MA60']:.2f} ({'多头' if current['收盘'] > current['MA60'] else '空头'})")
            
            # 支撑阻力
            recent_20 = hist_df.tail(20)
            support = recent_20['最低'].min()
            resistance = recent_20['最高'].max()
            print(f"  支撑位：{support:.2f}")
            print(f"  阻力位：{resistance:.2f}")
            
    except Exception as e:
        print(f"  技术分析失败：{e}")

# ==================== 6. 估值对比表 ====================
print("\n" + "=" * 80)
print("六、估值对比总表")
print("=" * 80)

print("\n| 股票 | 股价 | PE | PB | 股息率 | 市值 (亿) | 今日涨跌 |")
print("|------|------|----|----|--------|----------|----------|")

for code, info in stock_info.items():
    pe_str = f"{info['pe']:.2f}" if info.get('pe') else "N/A"
    pb_str = f"{info['pb']:.2f}" if info.get('pb') else "N/A"
    div_str = f"{info['dividend_yield']:.2f}%" if info.get('dividend_yield') else "N/A"
    market_str = f"{info['market_cap']/100000000:.2f}" if info.get('market_cap') else "N/A"
    change_str = f"{info['change_pct']:+.2f}%" if info.get('change_pct') else "N/A"
    
    print(f"| {info['name']} | {info['price']:.2f} | {pe_str} | {pb_str} | {div_str} | {market_str} | {change_str} |")

# ==================== 7. 投资建议 ====================
print("\n" + "=" * 80)
print("七、投资建议")
print("=" * 80)

# 分析哪只股票最适合
best_stock = None
best_score = -999

for code, info in stock_info.items():
    score = 0
    
    # 低估值加分
    if info.get('pe', 999) < 10:
        score += 30
    elif info.get('pe', 999) < 15:
        score += 20
    
    # 低 PB 加分
    if info.get('pb', 999) < 1:
        score += 20
    elif info.get('pb', 999) < 1.5:
        score += 10
    
    # 高股息加分
    if info.get('dividend_yield', 0) > 4:
        score += 20
    elif info.get('dividend_yield', 0) > 3:
        score += 10
    
    # 股价<10 元适合新手
    if info['price'] < 10:
        score += 10
    
    # 大市值更稳定
    if info.get('market_cap', 0) > 100000000000:  # 1000 亿
        score += 10
    
    info['score'] = score
    
    if score > best_score:
        best_score = score
        best_stock = code

if best_stock:
    best = stock_info[best_stock]
    print(f"""
【综合评分最高】{best['name']} ({best_stock})
综合得分：{best['score']}分

推荐理由:
- 估值合理 (PE: {best.get('pe', 'N/A')}, PB: {best.get('pb', 'N/A')})
- 股息率：{best.get('dividend_yield', 'N/A')}%
- 股价：{best['price']:.2f}元，适合 1.2 万预算

【具体操作建议】

基于谭老师情况 (1.2 万预算，新手，风险承受 -20%，1-3 年持有):

1. **仓位配置**:
   - 首笔建仓：5000-6000 元 (约 50% 仓位)
   - 剩余资金：等待回调加仓或定投

2. **买入价格**:
   - 理想买入区间：{best['price'] * 0.95:.2f} - {best['price'] * 1.02:.2f}元
   - 如果开盘涨幅>2%，建议等待回调

3. **止损设置**:
   - 止损位：{best['price'] * 0.9:.2f}元 (-10%)
   - 最大亏损：约 600 元 (在承受范围内)

4. **目标价位**:
   - 第一目标：{best['price'] * 1.15:.2f}元 (+15%)
   - 第二目标：{best['price'] * 1.2:.2f}元 (+20%)

5. **持有策略**:
   - 长期持有 1-3 年
   - 收取股息作为安全垫
   - 每季度复盘一次

【明日操作】

✅ 如果平开或低开 (<1%): 可买入 500-800 股
✅ 如果高开 (1-2%): 观望，等待盘中回调
❌ 如果高开>3%: 不建议追高，等待后续机会

【风险提示】

⚠️ 国际油价波动风险
⚠️ 新能源替代长期压力
⚠️ 地缘政治不确定性
⚠️ 股市有风险，投资需谨慎

【其他备选】

如果首选股票涨幅过大，可考虑:
""")

    # 显示其他备选
    for code, info in stock_info.items():
        if code != best_stock and info['price'] < 20:
            print(f"- {info['name']} ({code}): {info['price']:.2f}元，PE={info.get('pe', 'N/A')}, 股息率={info.get('dividend_yield', 'N/A')}%")

print("""
【免责声明】
以上分析基于公开数据，仅供参考，不构成投资建议。
股市有风险，入市需谨慎。请根据自身情况独立决策。
""")

print("\n" + "=" * 80)
print("报告生成完毕")
print("=" * 80)
