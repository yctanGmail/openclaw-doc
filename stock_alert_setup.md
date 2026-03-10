# 股票价格预警系统 - 配置说明

## ✅ 已创建文件

1. `stock_alert.py` - 监控脚本
2. `stock_alert_cron.txt` - Cron 定时配置

## 🔧 需要配置：飞书 Webhook

### 步骤 1：创建飞书机器人

1. 打开飞书群聊（或创建新群）
2. 点击右上角「…」→「添加机器人」
3. 选择「自定义机器人」
4. 设置机器人名称（如：股票预警助手）
5. 复制 **Webhook 地址**

### 步骤 2：设置环境变量

编辑 `~/.bashrc` 或 `~/.profile`，添加：

```bash
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
```

然后执行：
```bash
source ~/.bashrc
```

### 步骤 3：测试脚本

```bash
cd /home/yctan/.openclaw/workspace-lead
python3 stock_alert.py
```

### 步骤 4：安装 Cron 任务

```bash
crontab -l > /tmp/my_cron.tmp
cat stock_alert_cron.txt >> /tmp/my_cron.tmp
crontab /tmp/my_cron.tmp
rm /tmp/my_cron.tmp
```

### 步骤 5：验证 Cron

```bash
crontab -l  # 查看已安装的 cron 任务
tail -f stock_alert.log  # 查看执行日志
```

## 📊 预警规则

| 涨跌幅 | 预警消息 |
|--------|----------|
| +7% 以上 | 建议减仓 |
| +5% 以上 | 考虑止盈 |
| -5% 以下 | 检查基本面 |
| -8% 以下 | 考虑止损 |

## 🕐 检查时间

- **上午：** 9:30, 9:45, 10:00, 10:15, 10:30, 10:45, 11:00, 11:15
- **下午：** 13:00, 13:15, 13:30, 13:45, 14:00, 14:15, 14:30, 14:45, 15:00
- **周末和节假日：** 自动跳过

## 📝 推送格式示例

```
🔔【价格预警】
股票：招商银行 (600036)
现价：40.85 元
涨跌：+5.0%
成本：38.90 元
成本涨跌：+5.0%
建议：考虑止盈
时间：2026-03-10 10:15:00
```

## ⚠️ 注意事项

1. 确保 Python 环境已安装 akshare：`pip3 install akshare`
2. 确保服务器时间正确（Asia/Shanghai 时区）
3. 日志文件：`stock_alert.log`
4. 如需修改持仓或成本价，编辑 `stock_alert.py` 中的 `HOLDINGS` 配置
