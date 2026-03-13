#!/bin/bash
# 股票预警 Cron 包装脚本
# 设置环境变量并执行 Python 脚本

cd /home/yctan/.openclaw/workspace-lead

# 记录日志
echo "=== 股票预警检查 $(date '+%Y-%m-%d %H:%M:%S') ===" >> stock_alert.log

# 执行 Python 脚本
/usr/bin/python3 stock_alert.py >> stock_alert.log 2>&1

echo "" >> stock_alert.log
