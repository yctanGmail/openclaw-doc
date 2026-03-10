#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股完整市场分析报告
使用新的 fetch_complete_stock_data() 函数获取完整数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os

# 添加父目录到路径以导入 evening_review_enhanced
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evening_review_enhanced import StockDataFetcher


def get_market_indices():
    """获取大盘指数数据"""
    print("\n正在获取大盘指数数据...")
    
    indices_data = []
    
    try:
        # 上证指数
        sh_index = ak.stock_zh_index_spot(symbol="sh000001")
        indices_data.append({
            'name': '上证指数',
            'close': sh_index['最新价'].values[0],
            'change_pct': sh_index['涨跌幅'].values[0],
            'volume': sh_index['成交量'].values[0],
            'amount': sh_index['成交额'].values[0]
        })
        
        # 深证成指
        sz_index = ak.stock_zh_index_spot(symbol="sz399001")
        indices_data.append({
            'name': '深证成指',
            'close': sz_index['最新价'].values[0],
            'change_pct': sz_index['涨跌幅'].values[0],
            'volume': sz_index['成交量'].values[0],
            'amount': sz_index['成交额'].values[0]
        })
        
        # 创业板指
        cy_index = ak.stock_zh_index_spot(symbol="sz399006")
        indices_data.append({
            'name': '创业板指',
            'close': cy_index['最新价'].values[0],
            'change_pct': cy_index['涨跌幅'].values[0],
            'volume': cy_index['成交量'].values[0],
            'amount': cy_index['成交额'].values[0]
        })
        
        print("  ✅ 大盘指数数据获取成功")
        
    except Exception as e:
        print(f"  ❌ 大盘指数数据获取失败：{e}")
    
    return indices_data


def analyze_stock(data, code, name):
    """分析个股数据并生成报告段落"""
    if data is None:
        return f"### {name} ({code})\n- 数据获取失败\n"
    
    report = f"### {name} ({code})\n\n"
    
    # 实时数据
    price = data.get('price')
    change_pct = data.get('change_pct')
    if price and change_pct is not None:
        sign = "+" if change_pct > 0 else ""
        report += f"- **实时数据：** {price:.2f} 元 ({sign}{change_pct:.2f}%)\n"
    
    # 成交量和成交额
    volume = data.get('volume')
    amount = data.get('amount')
    if volume:
        volume_wan = volume / 10000  # 转换为万手
        report += f"- **成交量：** {volume_wan:.2f} 万手\n"
    if amount:
        amount_yi = amount / 100000000  # 转换为亿元
        report += f"- **成交额：** {amount_yi:.2f} 亿元\n"
    
    # 估值指标
    pe_ttm = data.get('pe_ttm')
    pb = data.get('pb')
    dividend = data.get('dividend')
    
    if pe_ttm:
        report += f"- **PE (TTM)：** {pe_ttm:.1f} 倍\n"
    if pb:
        report += f"- **PB：** {pb:.1f} 倍\n"
    if dividend is not None:
        report += f"- **股息率：** {dividend:.2f}%\n"
    
    # 资金流向
    main_flow = data.get('main_flow')
    if main_flow is not None:
        main_flow_yi = main_flow / 10000  # 转换为亿元
        flow_direction = "流入" if main_flow > 0 else "流出"
        report += f"- **主力流向：** {abs(main_flow_yi):.2f} 亿元{flow_direction}\n"
    
    # 技术面
    ma5 = data.get('ma5')
    support = data.get('support')
    resistance = data.get('resistance')
    rsi = data.get('rsi')
    
    tech_parts = []
    if ma5:
        tech_parts.append(f"5 日线 {ma5:.2f} 元")
    if support:
        tech_parts.append(f"支撑位 {support:.2f} 元")
    if resistance:
        tech_parts.append(f"阻力位 {resistance:.2f} 元")
    if rsi:
        rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "中性"
        tech_parts.append(f"RSI {rsi:.2f}({rsi_status})")
    
    if tech_parts:
        report += f"- **技术面：** {', '.join(tech_parts)}\n"
    
    return report


def generate_trading_strategy(stocks_data):
    """生成明日策略建议"""
    strategy = "## 明日策略\n\n"
    
    strategy += "### 大盘判断\n"
    strategy += "- 当前市场处于震荡整理阶段，建议控制仓位在 6-7 成\n"
    strategy += "- 关注成交量变化，若持续缩量需谨慎\n"
    strategy += "- 重点关注北向资金流向，作为短期风向标\n\n"
    
    strategy += "### 持仓股操作建议\n\n"
    
    # 招商银行分析
    cm_data = stocks_data.get('600036')
    if cm_data and cm_data.get('price'):
        price = cm_data['price']
        pe = cm_data.get('pe_ttm', 0)
        pb = cm_data.get('pb', 0)
        ma5 = cm_data.get('ma5')
        
        strategy += "**招商银行 (600036)：**\n"
        
        # 估值判断
        if pe and pe < 7:
            strategy += "- ✅ 估值处于历史低位，PE 仅" + f"{pe:.1f}" + "倍，具备安全边际\n"
        if pb and pb < 1:
            strategy += "- ✅ PB 低于 1，破净状态，长期配置价值凸显\n"
        
        # 技术面判断
        if ma5 and price:
            if price > ma5:
                strategy += "- 📈 股价站上 5 日线，短期趋势向好\n"
            else:
                strategy += "- 📉 股价低于 5 日线，短期承压\n"
        
        # 操作建议
        strategy += "- **操作：** 逢低吸纳，分批建仓\n"
        strategy += "- **目标价：** 42-45 元（对应 1.0-1.1 倍 PB）\n"
        strategy += "- **止损位：** 35 元（前低支撑）\n\n"
    
    # 紫金矿业分析
    zj_data = stocks_data.get('601899')
    if zj_data and zj_data.get('price'):
        price = zj_data['price']
        pe = zj_data.get('pe_ttm', 0)
        ma5 = zj_data.get('ma5')
        main_flow = zj_data.get('main_flow', 0)
        
        strategy += "**紫金矿业 (601899)：**\n"
        
        # 估值判断
        if pe:
            if pe < 15:
                strategy += "- ✅ 估值合理，PE " + f"{pe:.1f}" + "倍处于行业中低位\n"
            else:
                strategy += "- ⚠️ 估值偏高，需警惕回调风险\n"
        
        # 资金流向
        if main_flow is not None:
            if main_flow > 0:
                strategy += "- 💰 主力资金净流入，市场认可度高\n"
            else:
                strategy += "- 💸 主力资金净流出，短期谨慎\n"
        
        # 技术面判断
        if ma5 and price:
            if price > ma5:
                strategy += "- 📈 股价站上 5 日线，趋势良好\n"
            else:
                strategy += "- 📉 股价低于 5 日线，等待企稳\n"
        
        # 操作建议
        strategy += "- **操作：** 持有为主，逢高可适当减仓\n"
        strategy += "- **目标价：** 40-42 元（前期高点）\n"
        strategy += "- **止损位：** 33 元（20 日线支撑）\n\n"
    
    strategy += "### 风险提示\n"
    strategy += "1. ⚠️ 全球经济不确定性增加，关注美联储政策动向\n"
    strategy += "2. ⚠️ 国内经济复苏力度仍需观察\n"
    strategy += "3. ⚠️ 地缘政治风险可能影响市场情绪\n"
    strategy += "4. ⚠️ 个股财报季临近，注意业绩波动风险\n\n"
    
    strategy += "### 重点关注\n"
    strategy += "- 📊 成交量变化：若沪指成交量持续低于 3000 亿，需谨慎\n"
    strategy += "- 💱 北向资金：连续 3 日净流入可加大仓位\n"
    strategy += "- 🏦 金融股动向：银行、保险企稳是市场止跌信号\n"
    
    return strategy


def main():
    """主函数：生成完整市场分析报告"""
    print("=" * 80)
    print("正在生成 A 股完整市场分析报告...")
    print("=" * 80)
    
    # 初始化数据获取器
    fetcher = StockDataFetcher()
    
    # 获取大盘数据
    indices_data = get_market_indices()
    time.sleep(1)
    
    # 持仓股列表
    holdings = {
        '600036': '招商银行',
        '601899': '紫金矿业'
    }
    
    # 获取持仓股完整数据
    stocks_data = {}
    for code, name in holdings.items():
        data = fetcher.fetch_complete_stock_data(code)
        if data:
            stocks_data[code] = data
        time.sleep(2)  # 避免请求过快
    
    # 生成报告
    report_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    report = f"# 📊 A 股完整市场分析报告\n\n"
    report += f"**生成时间：** {report_time}\n\n"
    
    # 大盘数据
    report += "## 大盘数据\n\n"
    report += "| 指数 | 收盘价 | 涨跌 | 成交量 | 成交额 |\n"
    report += "|------|--------|------|--------|--------|\n"
    
    for idx in indices_data:
        close = idx['close']
        change = idx['change_pct']
        volume = idx['volume'] / 100000000  # 转换为亿
        amount = idx['amount'] / 100000000  # 转换为亿
        sign = "+" if change > 0 else ""
        report += f"| {idx['name']} | {close:.2f} | {sign}{change:.2f}% | {volume:.2f} 亿 | {amount:.2f} 亿 |\n"
    
    report += "\n"
    
    # 持仓股深度分析
    report += "## 持仓股深度分析\n\n"
    
    for code, name in holdings.items():
        data = stocks_data.get(code)
        report += analyze_stock(data, code, name)
        report += "\n"
    
    # 明日策略
    report += generate_trading_strategy(stocks_data)
    
    # 输出报告
    print("\n" + "=" * 80)
    print("报告生成完成！")
    print("=" * 80)
    print(report)
    
    # 保存到文件
    output_file = f"/home/yctan/.openclaw/workspace-lead/reports/market_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存至：{output_file}")
    print("=" * 80)
    
    return report


if __name__ == "__main__":
    main()
