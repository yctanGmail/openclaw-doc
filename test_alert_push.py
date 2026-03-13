#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票预警推送功能
"""

import subprocess
import sys

# 测试消息
TEST_MESSAGE = """🔔 【价格预警】
股票：招商银行 (600036)
现价：40.50 元
涨跌：+5.20%
成本：38.90 元
成本涨跌：+4.11%
建议：考虑止盈"""

def main():
    print("=== 测试股票预警推送 ===")
    print(f"测试消息:\n{TEST_MESSAGE}\n")
    
    # 使用 openclaw message 发送测试消息
    try:
        result = subprocess.run(
            ["openclaw", "message", "send", "--channel", "feishu", "--message", TEST_MESSAGE],
            capture_output=True,
            text=True,
            cwd="/home/yctan/.openclaw/workspace-lead"
        )
        
        if result.returncode == 0:
            print("✅ 推送成功!")
            print(f"输出：{result.stdout}")
        else:
            print("❌ 推送失败")
            print(f"错误：{result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 执行失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
