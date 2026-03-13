# 持仓股票价格预警系统

## 监控股票

| 股票 | 代码 | 成本价 |
|------|------|--------|
| 招商银行 | 600036 | 38.90 元 |
| 紫金矿业 | 601899 | 35.12 元 |

## 预警规则

基于**成本价**的涨跌幅触发预警：

| 涨跌幅 | 预警级别 | 推送建议 |
|--------|----------|----------|
| +7% | 🔴 高危 | 建议减仓 |
| +5% | 🟠 中危 | 考虑止盈 |
| -5% | 🟡 警示 | 检查基本面 |
| -8% | 🔴 高危 | 考虑止损 |

## 检查频率

- **时间**: 交易日 9:30-11:30, 13:00-15:00
- **间隔**: 每 15 分钟
- **推送**: 仅触发预警时推送（每日每只股票每级别只推一次）

## 文件说明

- `stock_alert.py` - 主脚本（检查价格 + 发送预警）
- `stock_alert_cron.sh` - Cron 包装脚本
- `stock_alert_state.json` - 预警状态记录（避免重复推送）
- `stock_alert.log` - 运行日志

## Cron 配置

```bash
# 交易时间每 15 分钟检查（周一至周五）
30,45 9 * * 1-5 /home/yctan/.openclaw/workspace-lead/stock_alert_cron.sh
0,15,30,45 10 * * 1-5 /home/yctan/.openclaw/workspace-lead/stock_alert_cron.sh
0,15,30 11 * * 1-5 /home/yctan/.openclaw/workspace-lead/stock_alert_cron.sh
0,15,30,45 13 * * 1-5 /home/yctan/.openclaw/workspace-lead/stock_alert_cron.sh
0,15,30 14 * * 1-5 /home/yctan/.openclaw/workspace-lead/stock_alert_cron.sh
0 15 * * 1-5 /home/yctan/.openclaw/workspace-lead/stock_alert_cron.sh
```

## 推送格式

```
🔔【价格预警】
股票：XXX
现价：XX 元
涨跌：+X%
成本涨跌：+X%
建议：XXX
```

## 手动测试

```bash
cd /home/yctan/.openclaw/workspace-lead
python3 stock_alert.py
```

## 查看日志

```bash
tail -f stock_alert.log
```

## 重置预警状态

删除状态文件即可重置：
```bash
rm stock_alert_state.json
```
