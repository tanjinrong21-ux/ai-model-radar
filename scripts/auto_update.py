#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""auto_update.py — cron 定时调用的自动更新入口。
每日执行：拉取 GitHub 星数 → 重建 data.js。供 Hermes cron 调用（no_agent）。
"""
import subprocess
import sys
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=== AI 情报站 自动更新 ===")
r = subprocess.run(
    [sys.executable, os.path.join(BASE, "scripts", "fetch_github.py"), "--build"],
    cwd=BASE,
)
sys.exit(r.returncode)
