#!/usr/bin/env python3
"""
增强版 GitHub 同步 + 推送通知
替代原来的简单同步脚本
"""

import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace-lead"
GITHUB_REPO = WORKSPACE / "openclaw-doc"
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
REPORTS_DIR = WORKSPACE / "reports"

# Git 配置
GIT_USER = "yctan"
GIT_EMAIL = "yctanGmail@gmail.com"
REMOTE_URL = "git@github.com:yctanGmail/openclaw-doc.git"


def log(message: str):
    """打印日志"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def ensure_repo_cloned():
    """确保仓库已克隆"""
    if not GITHUB_REPO.exists():
        log("📦 克隆 GitHub 仓库...")
        subprocess.run(
            ["git", "clone", REMOTE_URL, str(GITHUB_REPO)],
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", GIT_USER],
            cwd=GITHUB_REPO,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", GIT_EMAIL],
            cwd=GITHUB_REPO,
            check=True,
            capture_output=True
        )
    log("✅ 仓库已就绪")


def sync_file(src: Path, dest: Path, category: str) -> bool:
    """同步单个文件"""
    if not src.exists():
        return False
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果文件已存在且内容相同，跳过
    if dest.exists():
        if src.read_bytes() == dest.read_bytes():
            return False
    
    shutil.copy2(src, dest)
    log(f"  📄 {category}: {src.name}")
    return True


def sync_all() -> dict:
    """同步所有文件，返回统计信息"""
    stats = {
        'memory': 0,
        'daily': 0,
        'reports': 0,
        'total': 0
    }
    
    # 同步 MEMORY.md
    if sync_file(MEMORY_FILE, GITHUB_REPO / "记忆系统" / "MEMORY.md", "记忆"):
        stats['memory'] = 1
        stats['total'] += 1
    
    # 同步每日记忆
    if MEMORY_DIR.exists():
        dest_dir = GITHUB_REPO / "记忆系统" / "日常记忆"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for file in MEMORY_DIR.glob("*.md"):
            if sync_file(file, dest_dir / file.name, "记忆"):
                stats['daily'] += 1
                stats['total'] += 1
    
    # 同步市场报告
    if REPORTS_DIR.exists():
        dest_dir = GITHUB_REPO / "市场报告"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for file in sorted(REPORTS_DIR.glob("*.md"), reverse=True)[:20]:
            if sync_file(file, dest_dir / file.name, "报告"):
                stats['reports'] += 1
                stats['total'] += 1
    
    return stats


def commit_and_push(stats: dict) -> bool:
    """提交并推送更改"""
    try:
        # 添加所有更改
        subprocess.run(
            ["git", "add", "-A"],
            cwd=GITHUB_REPO,
            check=True,
            capture_output=True
        )
        
        # 检查是否有更改
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=GITHUB_REPO,
            capture_output=True
        )
        if result.returncode == 0:
            log("ℹ️  没有更改，跳过提交")
            return False
        
        # 构建提交信息
        messages = []
        if stats['memory'] > 0:
            messages.append("MEMORY.md")
        if stats['daily'] > 0:
            messages.append(f"{stats['daily']} 个记忆文件")
        if stats['reports'] > 0:
            messages.append(f"{stats['reports']} 个报告")
        
        commit_msg = f"🔄 自动同步：{', '.join(messages)}\n\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 提交
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=GITHUB_REPO,
            check=True,
            capture_output=True
        )
        
        # 推送
        log("📤 推送到 GitHub...")
        subprocess.run(
            ["git", "push"],
            cwd=GITHUB_REPO,
            check=True,
            capture_output=True,
            timeout=30
        )
        
        log("✅ 推送成功")
        return True
        
    except subprocess.CalledProcessError as e:
        log(f"❌ Git 操作失败：{e}")
        return False
    except subprocess.TimeoutExpired:
        log("❌ Git 推送超时")
        return False


def generate_summary(stats: dict) -> str:
    """生成同步摘要"""
    if stats['total'] == 0:
        return "ℹ️  没有需要同步的内容"
    
    lines = ["✅ **GitHub 同步完成**\n"]
    lines.append(f"**同步时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("**同步内容：**")
    
    if stats['memory'] > 0:
        lines.append("- ✅ MEMORY.md")
    if stats['daily'] > 0:
        lines.append(f"- ✅ {stats['daily']} 个记忆文件")
    if stats['reports'] > 0:
        lines.append(f"- ✅ {stats['reports']} 个市场报告")
    
    lines.append("")
    lines.append(f"**总计：** {stats['total']} 个文件")
    lines.append("")
    lines.append(f"🔗 **仓库：** https://github.com/yctanGmail/openclaw-doc")
    
    return "\n".join(lines)


def main():
    """主函数"""
    print("=" * 60)
    print("🔄 GitHub 投资文档同步（增强版）")
    print(f"⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 确保仓库已克隆
    ensure_repo_cloned()
    
    # 同步文件
    log("开始同步文件...")
    stats = sync_all()
    
    # 提交并推送
    if stats['total'] > 0:
        if commit_and_push(stats):
            summary = generate_summary(stats)
            print("\n" + summary)
        else:
            log("❌ 推送失败")
    else:
        log("ℹ️  没有需要同步的内容")
    
    print("=" * 60)
    print("✅ 同步完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
