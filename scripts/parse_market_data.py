#!/usr/bin/env python3
"""
解析腾讯财经 API 数据并生成复盘报告
数据来源：http://qt.gtimg.cn/
时间戳：2026-03-10 16:14 (收盘后)
"""

# 腾讯财经 API 原始数据
raw_data = """
v_sh000001="1~上证指数~000001~4123.14~4096.60~4098.59~674922194~0~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~~20260310161415~26.54~0.65~4123.96~4098.59~4123.14/674922194/1036427205293~674922194~103642721~1.41~17.55~~4123.96~4098.59~0.62~634011.38~675761.73~0.00~-1~-1~0.88~0~4112.12~~~~~~103642720.5293~0.0000~0~ ~ZS~3.89~0.01~~~~4197.23~3040.69~0.14~2.67~6.38~4789693404904~~-3.83~21.19~4789693404904~~~22.49~0.01~~CNY~0~~0.00~0~";
v_sz399001="51~深证成指~399001~14354.07~14067.50~14239.30~736222902~0~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~~20260310161436~286.57~2.04~14357.82~14239.30~14354.07/736222902/1361460406127~736222902~136146041~3.05~53.56~~14357.82~14239.30~0.84~403478.35~471191.07~0.00~-1~-1~0.91~0~14298.29~~~~~~136146040.6127~0.0000~0~ ~ZS~6.13~2.37~~~~14536.08~9119.60~0.44~3.83~10.36~2414693173655~~-12.40~40.09~2414693173655~~~32.59~0.00~~CNY~0~~0.00~0~";
v_sz399006="51~创业板指~399006~3306.14~3208.58~3281.94~236304274~0~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~~20260310161451~97.56~3.04~3308.75~3272.99~3306.14/236304274/644901557426~236304274~64490156~4.55~71.22~~3308.75~3272.99~1.11~152685.32~189089.78~0.00~-1~-1~0.97~0~3291.18~~~~~~64490155.7426~0.0000~0~ ~ZS~3.21~3.01~~~~3416.84~1756.64~-0.06~1.29~7.78~519626299564~~-16.99~60.35~519626299564~~~50.29~0.00~~CNY~0~~0.00~0~";
v_sh600036="1~招商银行~600036~39.22~38.79~38.94~613717~343525~270192~39.22~976~39.21~44~39.20~105~39.19~231~39.18~72~39.23~3074~39.24~3623~39.25~4703~39.26~1254~39.27~1941~~20260310161425~0.43~1.11~39.24~38.80~39.22/613717/2399803866~613717~239980~0.30~6.59~~39.24~38.80~1.13~8090.67~9891.22~0.90~42.67~34.91~0.67~-13167~39.10~6.59~6.59~~~0.42~239980.3866~0.0000~0~ ~GP-A~-4.54~0.10~7.68~11.76~1.19~45.54~36.38~0.72~2.00~-7.08~20628944429~25219845601~-82.18~-7.27~20628944429~~~-2.09~0.05~~CNY~0~___D__F__N~39.30~-4762~";
v_sh601899="1~紫金矿业~601899~37.13~36.40~36.98~2013124~980776~1032348~37.13~4067~37.12~721~37.11~1136~37.10~1433~37.09~815~37.14~3256~37.15~4299~37.16~1846~37.17~746~37.18~1267~~20260310161419~0.73~2.01~37.54~36.80~37.13/2013124/7475371505~2013124~747537~0.98~21.67~~37.54~36.80~2.03~7649.11~9872.77~5.88~40.04~32.76~0.62~-3242~37.13~19.56~30.80~~~1.84~747537.1505~0.0000~0~ ~GP-A~7.72~-4.45~1.34~26.91~11.47~44.94~14.69~-5.57~1.42~20.98~20600893140~26589733140~-16.55~104.46~20600893140~~~129.91~0.05~~CNY~0~___D__F__N~37.20~-4029~";
v_sh600028="1~中国石化~600028~6.56~7.00~6.50~6425513~2708533~3716980~6.56~23416~6.55~19310~6.54~42065~6.53~33355~6.52~37613~6.57~14629~6.58~7356~6.59~9338~6.60~18761~6.61~6642~~20260310161418~-0.44~-6.29~6.62~6.47~6.56/6425513/4201781392~6425513~420178~0.68~22.00~~6.62~6.47~2.14~6215.76~7932.71~0.96~7.70~6.30~0.62~99033~6.54~19.84~15.77~~~0.49~420178.1392~0.0000~0~ ~GP-A~6.15~-16.11~3.48~4.34~1.87~8.11~5.02~-0.30~2.82~9.88~94752475375~120925514222~46.61~16.27~94752475375~~~20.10~0.15~~CNY~0~___D__F__N~6.50~153006~";
v_sh512710="1~军工龙头 ETF~512710~0.879~0.866~0.866~6332680~2974458~3358222~0.878~36123~0.877~22195~0.876~24027~0.875~12772~0.874~9571~0.879~38278~0.880~87335~0.881~32217~0.882~34905~0.883~14268~~20260310161441~0.013~1.50~0.892~0.866~0.879/6332680/557022816~6332680~55702~4.96~~~0.892~0.866~3.00~112.25~112.25~0.00~0.953~0.779~0.60~-102315~0.880~~~~~~55702.2816~0.0000~0~ ~ETF~12.12~2.45~~~~0.985~0.536~1.38~7.33~32.58~12769658400~12769658400~-32.83~39.75~12769658400~-0.05~0.8794~40.19~0.11~0.8654~CNY~0~___D__F__N~0.888~-41346~";
"""

# 持仓信息
holdings = {
    '600036': {'name': '招商银行', 'shares': 200, 'cost': 39.005},
    '601899': {'name': '紫金矿业', 'shares': 100, 'cost': 35.20},
    '600028': {'name': '中国石化', 'shares': 100, 'cost': 6.55},
    '512710': {'name': '军工龙头 ETF', 'shares': 400, 'cost': 0.869},
}

# 解析数据
def parse_stock_data(line):
    """解析单只股票/指数的数据"""
    # 提取引号内的内容
    start = line.find('"') + 1
    end = line.rfind('"')
    data_str = line[start:end]
    
    # 按~分割
    parts = data_str.split('~')
    
    # 腾讯财经 API 字段说明 (根据实际数据分析):
    # 0: type (1=股票，51=指数)
    # 1: name
    # 2: code
    # 3: close (收盘价)
    # 4: prev_close (昨收)
    # 5: open (今开)
    # 6: volume (成交量)
    # ...
    # 27: 时间戳后的数据
    # 对于股票，在 ~~20260310161425~ 之后:
    #   - 涨跌额
    #   - 涨跌幅
    #   - 最高价
    #   - 最低价
    
    # 找到时间戳位置
    timestamp_idx = None
    for i, part in enumerate(parts):
        if part.startswith('20260310'):
            timestamp_idx = i
            break
    
    if timestamp_idx is None:
        # 尝试找其他年份的时间戳
        for i, part in enumerate(parts):
            if len(part) == 14 and part.isdigit():
                timestamp_idx = i
                break
    
    # 根据数据分析，最高价和最低价在时间戳后的第 3 和第 4 个位置
    # 例如 v_sh600036: ~~20260310161425~0.43~1.11~39.24~38.80~
    # 0.43=涨跌额，1.11=涨跌幅%，39.24=最高，38.80=最低
    
    high = None
    low = None
    
    if timestamp_idx:
        try:
            high = float(parts[timestamp_idx + 3])
            low = float(parts[timestamp_idx + 4])
        except (IndexError, ValueError):
            pass
    
    return {
        'type': parts[0],
        'name': parts[1],
        'code': parts[2],
        'close': float(parts[3]),
        'prev_close': float(parts[4]),
        'open': float(parts[5]),
        'volume': int(parts[6]),
        'high': high,
        'low': low,
        'timestamp_idx': timestamp_idx,
    }

# 解析所有数据
indices = {}
stocks = {}

for line in raw_data.strip().split('\n'):
    if not line.strip():
        continue
    
    data = parse_stock_data(line)
    code = data['code']
    
    # 调试输出
    print(f"解析 {data['name']} ({code}): 收盘={data['close']}, 最高={data['high']}, 最低={data['low']}, timestamp_idx={data['timestamp_idx']}")
    
    if code in ['000001', '399001', '399006']:
        indices[code] = data
    else:
        stocks[code] = data

# 计算涨跌幅
def calc_change_rate(close, prev_close):
    return (close - prev_close) / prev_close * 100

# 添加涨跌幅
for code, data in indices.items():
    data['change_pct'] = calc_change_rate(data['close'], data['prev_close'])

for code, data in stocks.items():
    data['change_pct'] = calc_change_rate(data['close'], data['prev_close'])

# 计算持仓盈亏
portfolio_summary = []
total_cost = 0
total_market_value = 0

for code, holding in holdings.items():
    stock_data = stocks[code]
    close = stock_data['close']
    shares = holding['shares']
    cost = holding['cost']
    
    position_cost = cost * shares
    market_value = close * shares
    profit = (close - cost) * shares
    profit_pct = (close - cost) / cost * 100
    
    portfolio_summary.append({
        'code': code,
        'name': holding['name'],
        'shares': shares,
        'cost': cost,
        'close': close,
        'change_pct': stock_data['change_pct'],
        'position_cost': position_cost,
        'market_value': market_value,
        'profit': profit,
        'profit_pct': profit_pct,
        'open': stock_data['open'],
        'high': stock_data['high'],
        'low': stock_data['low'],
        'volume': stock_data['volume'],
    })
    
    total_cost += position_cost
    total_market_value += market_value

total_profit = total_market_value - total_cost
total_profit_pct = total_profit / total_cost * 100

# 生成报告
report = f"""# 📊 A 股盘后复盘（2026-03-10）

> **数据来源：** 腾讯财经 API (http://qt.gtimg.cn/)  
> **数据时间：** 2026-03-10 16:14 (收盘后)  
> **生成时间：** 2026-03-10 19:30 GMT+8

---

## 大盘表现

| 指数 | 收盘 | 涨跌 |
|------|------|------|
| 上证指数 | {indices['000001']['close']:.2f} 点 | {indices['000001']['change_pct']:+.2f}% |
| 深证成指 | {indices['399001']['close']:.2f} 点 | {indices['399001']['change_pct']:+.2f}% |
| 创业板指 | {indices['399006']['close']:.2f} 点 | {indices['399006']['change_pct']:+.2f}% |

---

## 持仓股表现

| 股票 | 收盘 | 涨跌 | 盈亏 |
|------|------|------|------|
| 招商银行 | {portfolio_summary[0]['close']:.2f} 元 | {portfolio_summary[0]['change_pct']:+.2f}% | {portfolio_summary[0]['profit']:+.2f} 元 |
| 紫金矿业 | {portfolio_summary[1]['close']:.2f} 元 | {portfolio_summary[1]['change_pct']:+.2f}% | {portfolio_summary[1]['profit']:+.2f} 元 |
| 中国石化 | {portfolio_summary[2]['close']:.2f} 元 | {portfolio_summary[2]['change_pct']:+.2f}% | {portfolio_summary[2]['profit']:+.2f} 元 |
| 军工龙头 ETF | {portfolio_summary[3]['close']:.3f} 元 | {portfolio_summary[3]['change_pct']:+.2f}% | {portfolio_summary[3]['profit']:+.2f} 元 |

---

## 持仓股详细数据

### 招商银行 (600036)
- 开盘：{portfolio_summary[0]['open']:.2f} 元
- 最高：{portfolio_summary[0]['high']:.2f} 元
- 最低：{portfolio_summary[0]['low']:.2f} 元
- 收盘：{portfolio_summary[0]['close']:.2f} 元
- 成交量：{portfolio_summary[0]['volume']:,} 手

### 紫金矿业 (601899)
- 开盘：{portfolio_summary[1]['open']:.2f} 元
- 最高：{portfolio_summary[1]['high']:.2f} 元
- 最低：{portfolio_summary[1]['low']:.2f} 元
- 收盘：{portfolio_summary[1]['close']:.2f} 元
- 成交量：{portfolio_summary[1]['volume']:,} 手

### 中国石化 (600028)
- 开盘：{portfolio_summary[2]['open']:.2f} 元
- 最高：{portfolio_summary[2]['high']:.2f} 元
- 最低：{portfolio_summary[2]['low']:.2f} 元
- 收盘：{portfolio_summary[2]['close']:.2f} 元
- 成交量：{portfolio_summary[2]['volume']:,} 手

### 军工龙头 ETF (512710)
- 开盘：{portfolio_summary[3]['open']:.3f} 元
- 最高：{portfolio_summary[3]['high']:.3f} 元
- 最低：{portfolio_summary[3]['low']:.3f} 元
- 收盘：{portfolio_summary[3]['close']:.3f} 元
- 成交量：{portfolio_summary[3]['volume']:,} 手

---

## 总盈亏

- **总投入：** {total_cost:.2f} 元
- **总市值：** {total_market_value:.2f} 元
- **总盈亏：** {total_profit:+.2f} 元
- **收益率：** {total_profit_pct:+.2f}%

---

## 计算明细

| 股票 | 持股 | 成本价 | 收盘价 | 盈亏金额 |
|------|------|--------|--------|----------|
| 招商银行 | {portfolio_summary[0]['shares']} 股 | {portfolio_summary[0]['cost']:.3f} 元 | {portfolio_summary[0]['close']:.2f} 元 | {portfolio_summary[0]['profit']:+.2f} 元 |
| 紫金矿业 | {portfolio_summary[1]['shares']} 股 | {portfolio_summary[1]['cost']:.2f} 元 | {portfolio_summary[1]['close']:.2f} 元 | {portfolio_summary[1]['profit']:+.2f} 元 |
| 中国石化 | {portfolio_summary[2]['shares']} 股 | {portfolio_summary[2]['cost']:.2f} 元 | {portfolio_summary[2]['close']:.2f} 元 | {portfolio_summary[2]['profit']:+.2f} 元 |
| 军工龙头 ETF | {portfolio_summary[3]['shares']} 股 | {portfolio_summary[3]['cost']:.3f} 元 | {portfolio_summary[3]['close']:.3f} 元 | {portfolio_summary[3]['profit']:+.2f} 元 |

**计算公式：**
- 个股盈亏 = (收盘价 - 成本价) × 股数
- 总盈亏 = 所有股票盈亏之和
- 收益率 = 总盈亏 / 总成本 × 100%

---

*报告由小探 (market) 生成，等待小甜心审核*
"""

print("\n" + "="*60)
print(report)

# 保存报告
import os
os.makedirs('/home/yctan/.openclaw/workspace-lead/reports', exist_ok=True)
with open('/home/yctan/.openclaw/workspace-lead/reports/2026-03-10 复盘.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("\n✅ 报告已保存至：/home/yctan/.openclaw/workspace-lead/reports/2026-03-10 复盘.md")
