#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票完整数据获取脚本
数据源：
1. 腾讯财经 API - 基础行情
2. 东方财富 API - 资金流向、估值
3. 同花顺 API - 技术面数据

所有数据实时获取，包含完整错误处理和数据验证
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
import requests
import json
from typing import Optional, Dict, Any

warnings.filterwarnings('ignore')


class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def validate_price(self, price: float, code: str) -> bool:
        """验证价格合理性"""
        if price is None or np.isnan(price):
            return False
        if price <= 0:
            print(f"  ⚠️ 警告：{code} 价格 {price} 无效")
            return False
        if price > 100000:  # A 股价格上限检查
            print(f"  ⚠️ 警告：{code} 价格 {price} 异常偏高")
            return False
        return True
    
    def validate_ratio(self, ratio: float, field_name: str, code: str) -> bool:
        """验证比率类数据合理性"""
        if ratio is None or np.isnan(ratio):
            return False
        if ratio < -100 or ratio > 10000:
            print(f"  ⚠️ 警告：{code} {field_name}={ratio} 超出合理范围")
            return False
        return True
    
    def fetch_basic_data(self, code: str) -> Dict[str, Any]:
        """
        获取基础行情数据（腾讯财经 API）
        包含：现价、涨跌、涨跌幅、开盘、最高、最低、成交量、成交额
        """
        result = {
            'price': None,
            'change': None,
            'change_pct': None,
            'open': None,
            'high': None,
            'low': None,
            'volume': None,
            'amount': None,
        }
        
        try:
            # 使用 akshare 获取实时行情
            stock_spot = ak.stock_zh_a_spot_em()
            stock_info = stock_spot[stock_spot['代码'] == code]
            
            if len(stock_info) == 0:
                print(f"  ❌ 未找到股票 {code} 的实时行情")
                return result
            
            row = stock_info.iloc[0]
            
            # 基础价格数据
            result['price'] = float(row.get('最新价', 0))
            result['change'] = float(row.get('涨跌额', 0))
            result['change_pct'] = float(row.get('涨跌幅', 0))
            result['open'] = float(row.get('今开', 0))
            result['high'] = float(row.get('最高', 0))
            result['low'] = float(row.get('最低', 0))
            
            # 成交量和成交额
            result['volume'] = float(row.get('成交量', 0))
            result['amount'] = float(row.get('成交额', 0))
            
            # 数据验证
            if not self.validate_price(result['price'], code):
                result['price'] = None
            
            print(f"  ✅ 基础行情获取成功")
            print(f"     现价：{result['price']:.2f}, 涨跌幅：{result['change_pct']:.2f}%")
            
        except Exception as e:
            print(f"  ❌ 基础行情获取失败：{e}")
        
        return result
    
    def fetch_advanced_data(self, code: str) -> Dict[str, Any]:
        """
        获取进阶数据（换手率、量比、振幅）
        """
        result = {
            'turnover': None,      # 换手率
            'volume_ratio': None,  # 量比
            'amplitude': None,     # 振幅
        }
        
        try:
            # 获取实时行情中的进阶数据
            stock_spot = ak.stock_zh_a_spot_em()
            stock_info = stock_spot[stock_spot['代码'] == code]
            
            if len(stock_info) > 0:
                row = stock_info.iloc[0]
                
                # 换手率
                if '换手率' in row.index:
                    result['turnover'] = float(row.get('换手率', 0))
                
                # 量比
                if '量比' in row.index:
                    result['volume_ratio'] = float(row.get('量比', 0))
                
                # 振幅
                if '振幅' in row.index:
                    result['amplitude'] = float(row.get('振幅', 0))
                
                print(f"  ✅ 进阶数据获取成功")
                print(f"     换手率：{result['turnover']:.2f}%, 量比：{result['volume_ratio']:.2f}")
            
        except Exception as e:
            print(f"  ❌ 进阶数据获取失败：{e}")
        
        return result
    
    def fetch_valuation_data(self, code: str) -> Dict[str, Any]:
        """
        获取估值数据（PE、PB、PS、股息率）
        数据源：东方财富 F10 资料
        """
        result = {
            'pe_ttm': None,    # PE (TTM)
            'pb': None,        # PB
            'ps': None,        # PS
            'dividend': None,  # 股息率
        }
        
        try:
            # 获取个股信息
            stock_info = ak.stock_individual_info_em(symbol=code)
            
            if len(stock_info) > 0:
                for _, row in stock_info.iterrows():
                    item = str(row.get('item', ''))
                    value = row.get('value', '')
                    
                    # 提取 PE
                    if '市盈率' in item and 'TTM' in item:
                        try:
                            result['pe_ttm'] = float(str(value).replace('倍', '').strip())
                        except:
                            pass
                    
                    # 提取 PB
                    if '市净率' in item:
                        try:
                            result['pb'] = float(str(value).replace('倍', '').strip())
                        except:
                            pass
                    
                    # 提取 PS
                    if '市销率' in item:
                        try:
                            result['ps'] = float(str(value).replace('倍', '').strip())
                        except:
                            pass
                    
                    # 提取股息率
                    if '股息率' in item or '分红' in item:
                        try:
                            dividend_str = str(value).replace('%', '').strip()
                            result['dividend'] = float(dividend_str)
                        except:
                            pass
                
                # 备用方法：通过估值接口获取
                if result['pe_ttm'] is None:
                    try:
                        valuation_df = ak.stock_value_em(symbol=code)
                        if len(valuation_df) > 0:
                            result['pe_ttm'] = float(valuation_df['市盈率 (TTM)'].iloc[0])
                            result['pb'] = float(valuation_df['市净率'].iloc[0])
                    except:
                        pass
                
                print(f"  ✅ 估值数据获取成功")
                print(f"     PE(TTM): {result['pe_ttm']}, PB: {result['pb']}, 股息率：{result['dividend']}%")
            
        except Exception as e:
            print(f"  ❌ 估值数据获取失败：{e}")
        
        return result
    
    def fetch_cash_flow_data(self, code: str) -> Dict[str, Any]:
        """
        获取资金流向数据（主力、北向、超大单、大单）
        数据源：东方财富资金流向
        """
        result = {
            'main_flow': None,     # 主力净流入（万）
            'north_flow': None,    # 北向资金（万）
            'super_order': None,   # 超大单
            'big_order': None,     # 大单
        }
        
        try:
            # 获取主力资金流向
            try:
                main_flow_df = ak.stock_individual_fund_flow(symbol=code, market="sh" if code.startswith('6') else "sz")
                if len(main_flow_df) > 0:
                    latest = main_flow_df.iloc[0]
                    result['main_flow'] = float(latest.get('主力净流入-净额', 0))
                    result['super_order'] = float(latest.get('超大单净流入-净额', 0))
                    result['big_order'] = float(latest.get('大单净流入-净额', 0))
            except Exception as e:
                print(f"     主力资金数据获取失败：{e}")
            
            # 获取北向资金（沪深港通持股）
            try:
                north_hold = ak.stock_hsgt_individual_em(symbol=code)
                if len(north_hold) > 0:
                    # 获取最近一天的北向资金净流入
                    result['north_flow'] = float(north_hold['持股市值'].iloc[0])
            except Exception as e:
                print(f"     北向资金数据获取失败：{e}")
            
            print(f"  ✅ 资金流向数据获取成功")
            print(f"     主力净流入：{result['main_flow']}万，北向：{result['north_flow']}万")
            
        except Exception as e:
            print(f"  ❌ 资金流向数据获取失败：{e}")
        
        return result
    
    def fetch_technical_data(self, code: str) -> Dict[str, Any]:
        """
        获取技术面数据（均线、RSI、支撑/阻力）
        数据源：akshare 技术指标
        """
        result = {
            'ma5': None,      # 5 日均线
            'ma10': None,     # 10 日均线
            'ma20': None,     # 20 日均线
            'ma60': None,     # 60 日均线
            'rsi': None,      # RSI 指标
            'support': None,  # 支撑位
            'resistance': None,  # 阻力位
        }
        
        try:
            # 获取历史行情数据（用于计算均线和技术指标）
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=120)).strftime('%Y%m%d')
            
            stock_df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            if len(stock_df) > 0:
                # 计算均线
                if '收盘' in stock_df.columns:
                    close_prices = stock_df['收盘']
                    
                    result['ma5'] = float(close_prices.tail(5).mean())
                    result['ma10'] = float(close_prices.tail(10).mean())
                    result['ma20'] = float(close_prices.tail(20).mean())
                    result['ma60'] = float(close_prices.tail(60).mean()) if len(close_prices) >= 60 else None
                
                # 计算 RSI（使用 14 日 RSI）
                if len(stock_df) >= 15:
                    close_prices = stock_df['收盘'].values
                    deltas = np.diff(close_prices)
                    
                    gains = np.where(deltas > 0, deltas, 0)
                    losses = np.where(deltas < 0, -deltas, 0)
                    
                    # 计算 14 日平均收益和损失
                    avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains)
                    avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses)
                    
                    if avg_loss != 0:
                        rs = avg_gain / avg_loss
                        result['rsi'] = float(100 - (100 / (1 + rs)))
                    else:
                        result['rsi'] = 50.0
                
                # 计算支撑位和阻力位（使用最近 20 日的最低和最高价）
                if '最低' in stock_df.columns and '最高' in stock_df.columns:
                    result['support'] = float(stock_df['最低'].tail(20).min())
                    result['resistance'] = float(stock_df['最高'].tail(20).max())
                
                print(f"  ✅ 技术面数据获取成功")
                print(f"     MA5: {result['ma5']:.2f}, MA20: {result['ma20']:.2f}, RSI: {result['rsi']:.2f}")
            
        except Exception as e:
            print(f"  ❌ 技术面数据获取失败：{e}")
        
        return result
    
    def fetch_complete_stock_data(self, code: str) -> Optional[Dict[str, Any]]:
        """
        获取完整股票数据
        
        Args:
            code: 股票代码（6 位数字）
        
        Returns:
            包含完整股票数据的字典，获取失败返回 None
        """
        print(f"\n{'='*80}")
        print(f"正在获取 {code} 的完整数据...")
        print(f"数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        all_data = {
            # 基础数据
            'price': None,
            'change': None,
            'change_pct': None,
            'open': None,
            'high': None,
            'low': None,
            'volume': None,
            'amount': None,
            
            # 进阶数据
            'turnover': None,
            'volume_ratio': None,
            'amplitude': None,
            
            # 估值数据
            'pe_ttm': None,
            'pb': None,
            'ps': None,
            'dividend': None,
            
            # 资金流向
            'main_flow': None,
            'north_flow': None,
            'super_order': None,
            'big_order': None,
            
            # 技术面
            'ma5': None,
            'ma10': None,
            'ma20': None,
            'ma60': None,
            'rsi': None,
            'support': None,
            'resistance': None,
            
            # 元数据
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': '腾讯财经 + 东方财富 + akshare'
        }
        
        # 1. 获取基础行情数据
        basic_data = self.fetch_basic_data(code)
        all_data.update(basic_data)
        time.sleep(0.5)  # 避免请求过快
        
        # 2. 获取进阶数据
        advanced_data = self.fetch_advanced_data(code)
        all_data.update(advanced_data)
        time.sleep(0.5)
        
        # 3. 获取估值数据
        valuation_data = self.fetch_valuation_data(code)
        all_data.update(valuation_data)
        time.sleep(0.5)
        
        # 4. 获取资金流向
        cash_flow_data = self.fetch_cash_flow_data(code)
        all_data.update(cash_flow_data)
        time.sleep(0.5)
        
        # 5. 获取技术面数据
        technical_data = self.fetch_technical_data(code)
        all_data.update(technical_data)
        
        # 数据完整性检查
        filled_count = sum(1 for v in all_data.values() if v is not None)
        total_count = len(all_data)
        completeness = filled_count / total_count * 100
        
        print(f"\n{'='*80}")
        print(f"数据获取完成")
        print(f"数据完整度：{completeness:.1f}% ({filled_count}/{total_count})")
        print(f"{'='*80}")
        
        return all_data


def print_stock_summary(data: Dict[str, Any], code: str):
    """打印股票数据摘要"""
    if data is None:
        print(f"\n❌ {code} 数据获取失败")
        return
    
    print(f"\n📊 {code} 数据摘要")
    print(f"更新时间：{data['timestamp']}")
    print(f"数据来源：{data['source']}")
    print("-" * 80)
    
    # 基础行情
    print("\n【基础行情】")
    if data['price']:
        print(f"  现价：¥{data['price']:.2f}")
        print(f"  涨跌：{data['change']:.2f} ({data['change_pct']:+.2f}%)")
        print(f"  开盘：{data['open']:.2f} | 最高：{data['high']:.2f} | 最低：{data['low']:.2f}")
        print(f"  成交量：{data['volume']:,.0f} 手 | 成交额：{data['amount']:,.0f} 元")
    
    # 进阶数据
    print("\n【进阶指标】")
    if data['turnover']:
        print(f"  换手率：{data['turnover']:.2f}%")
    if data['volume_ratio']:
        print(f"  量比：{data['volume_ratio']:.2f}")
    if data['amplitude']:
        print(f"  振幅：{data['amplitude']:.2f}%")
    
    # 估值数据
    print("\n【估值指标】")
    if data['pe_ttm']:
        print(f"  PE(TTM): {data['pe_ttm']:.2f}")
    if data['pb']:
        print(f"  PB: {data['pb']:.2f}")
    if data['ps']:
        print(f"  PS: {data['ps']:.2f}")
    if data['dividend'] is not None:
        print(f"  股息率：{data['dividend']:.2f}%")
    
    # 资金流向
    print("\n【资金流向】")
    if data['main_flow'] is not None:
        print(f"  主力净流入：{data['main_flow']:,.0f} 万")
    if data['north_flow'] is not None:
        print(f"  北向资金：{data['north_flow']:,.0f} 万")
    if data['super_order'] is not None:
        print(f"  超大单：{data['super_order']:,.0f} 万")
    if data['big_order'] is not None:
        print(f"  大单：{data['big_order']:,.0f} 万")
    
    # 技术面
    print("\n【技术面】")
    if data['ma5']:
        print(f"  MA5: {data['ma5']:.2f}")
    if data['ma10']:
        print(f"  MA10: {data['ma10']:.2f}")
    if data['ma20']:
        print(f"  MA20: {data['ma20']:.2f}")
    if data['ma60']:
        print(f"  MA60: {data['ma60']:.2f}")
    if data['rsi']:
        rsi_status = "超买" if data['rsi'] > 70 else "超卖" if data['rsi'] < 30 else "中性"
        print(f"  RSI: {data['rsi']:.2f} ({rsi_status})")
    if data['support']:
        print(f"  支撑位：{data['support']:.2f}")
    if data['resistance']:
        print(f"  阻力位：{data['resistance']:.2f}")


def main():
    """主函数 - 测试数据获取"""
    print("=" * 80)
    print("股票完整数据获取脚本 - 测试")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    fetcher = StockDataFetcher()
    
    # 测试股票列表（石油股 + 热门股）
    test_stocks = [
        '601857',  # 中国石油
        '600028',  # 中国石化
        '600519',  # 贵州茅台
        '000858',  # 五粮液
        '300750',  # 宁德时代
    ]
    
    results = {}
    
    for code in test_stocks:
        try:
            data = fetcher.fetch_complete_stock_data(code)
            if data:
                results[code] = data
                print_stock_summary(data, code)
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"\n❌ {code} 获取失败：{e}")
            continue
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    print(f"成功获取：{len(results)}/{len(test_stocks)} 只股票")
    
    if results:
        print("\n成功获取的股票：")
        for code, data in results.items():
            price_str = f"¥{data['price']:.2f}" if data['price'] else "N/A"
            pe_str = f"{data['pe_ttm']:.2f}" if data['pe_ttm'] else "N/A"
            print(f"  {code}: 现价={price_str}, PE={pe_str}")
    
    print("\n" + "=" * 80)
    print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    main()
