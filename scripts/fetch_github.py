#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_github.py — 自动更新 skills.json / tools.json 的 GitHub 星数。
用法：python scripts/fetch_github.py [--build]
  - 读取 data/skills.json 与 data/tools.json 中的 repo
  - 用 gh api 实时查询 stargazers_count（已认证，5000次/小时）
  - 写回 JSON，记录更新时间
  - --build 时随后执行 build.py 重新生成 data.js
数据源：GitHub API（gh CLI）
"""
import json
import os
import shutil
import subprocess
import sys
import datetime
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")

# gh CLI 路径（本地 fallback；GitHub Actions 环境用 GITHUB_TOKEN）
GH = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"


def gh_stars(repo):
    """查询仓库星数，失败返回 (repo, None)。
    GitHub Actions 环境用 GITHUB_TOKEN 直调 API；本地用 gh CLI。"""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{repo}",
                headers={"Authorization": f"Bearer {token}", "User-Agent": "ai-model-radar/1.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode("utf-8"))
            return (repo, d.get("stargazers_count"))
        except Exception as e:
            print(f"  [WARN] {repo} 查询失败: {e}")
            return (repo, None)
    try:
        r = subprocess.run(
            [GH, "api", f"repos/{repo}", "--jq", ".stargazers_count"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return (repo, int(r.stdout.strip()))
    except Exception as e:
        print(f"  [WARN] {repo} 查询失败: {e}")
    return (repo, None)


def update_file(name, list_key):
    p = os.path.join(DATA_DIR, name)
    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    items = [it for it in data[list_key] if it.get("repo")]

    # 并发查询星数（gh api 串行太慢，65 个 repo 用 8 线程并发）
    print(f"  [fetch] 并发查询 {len(items)} 个 repo 星数…")
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = dict(ex.map(gh_stars, [it["repo"] for it in items]))

    changed = 0
    for item in items:
        repo = item["repo"]
        new_stars = results.get(repo)
        if new_stars is not None:
            if item.get("stars") != new_stars:
                changed += 1
            item["stars"] = new_stars
        else:
            print(f"  {repo:36s} ⭐ 查询失败(保留原值 {item.get('stars')})")

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    data["_meta"]["source"] = f"GitHub API (gh) 实查 — {now}"
    data["_meta"]["updated"] = now

    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] {name} 更新完成，{changed} 个星数变化")
    return changed


def main():
    build = "--build" in sys.argv
    print("=== fetch_github.py — GitHub 星数自动更新 ===")
    update_file("skills.json", "skills")
    update_file("tools.json", "tools")

    if build:
        print("\n=== 执行 build.py 重新生成 data.js ===")
        subprocess.run([sys.executable, os.path.join(BASE, "scripts", "build.py")])


if __name__ == "__main__":
    main()
