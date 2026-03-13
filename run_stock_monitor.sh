#!/bin/bash
# 股票价格预警监控运行脚本

# 设置环境变量
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"

# 切换到脚本目录
cd /home/yctan/.openclaw/workspace-lead

# 运行监控脚本
python3 stock_price_monitor.py >> stock_monitor.log 2>&1
