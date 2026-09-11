#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_models.py — 自动刷新模型数据（价格 + 综合/逻辑 benchmark + 上下文 + 模态 + 汇率）。
数据源：
  - 价格 + AA Index + GPQA：aiapiindex.com/prices.json（CC BY 4.0，公开数据）
  - 汇率：open.er-api.com（USD→CNY）
用法：python scripts/fetch_models.py
本地与 GitHub Actions 均可运行（纯 urllib，无 gh/curl 依赖）。
只更新可自动的字段（price/overall/logic/ctx/modality/fx），人工字段（access/homepage/docs/ppt_html/vision/audio/coding）不动。
"""
import json
import os
import sys
import urllib.request
import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")

PRICES_URL = "https://aiapiindex.com/prices.json"
FX_URL = "https://open.er-api.com/v6/latest/USD"

# 模型名映射：models.json 的 name -> prices.json 的 name（处理少数命名差异）
NAME_ALIAS = {
    "文心 ERNIE 5.1": "ERNIE 5.1",
}


def http_get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "ai-model-radar/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    print("=== fetch_models.py — 模型数据自动刷新 ===")

    # 1. 拉 prices.json
    try:
        prices = http_get_json(PRICES_URL)
        llm = prices.get("llm", [])
        asof = prices.get("asOf", {}).get("llm", "?")
        print(f"[OK] prices.json 拉取成功，{len(llm)} 个模型，asOf={asof}")
    except Exception as e:
        print(f"[WARN] prices.json 拉取失败，跳过模型数据刷新: {e}")
        llm, asof = [], None

    # 2. 拉汇率
    fx, fx_date = None, None
    try:
        fxd = http_get_json(FX_URL)
        fx = fxd.get("rates", {}).get("CNY")
        fx_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        print(f"[OK] 汇率拉取成功：1 USD = {fx} CNY")
    except Exception as e:
        print(f"[WARN] 汇率拉取失败，保留原值: {e}")

    # 3. 读 models.json
    mp = os.path.join(DATA_DIR, "models.json")
    with open(mp, encoding="utf-8") as f:
        data = json.load(f)

    # 建 name -> prices 条目 的索引
    prices_by_name = {p.get("name"): p for p in llm if p.get("name")}

    updated = 0
    for m in data["models"]:
        prices_name = NAME_ALIAS.get(m["name"], m["name"])
        pm = prices_by_name.get(prices_name)
        if not pm:
            print(f"  [SKIP] {m['name']} 未在 prices.json 找到")
            continue

        changed = False

        # 价格
        if pm.get("inPrice") is not None and pm.get("outPrice") is not None:
            new_price = {"in": pm["inPrice"], "out": pm["outPrice"]}
            if m.get("price") != new_price:
                m["price"] = new_price
                changed = True

        bench = pm.get("bench") or {}
        # 综合 = AA Index
        if bench.get("aa") is not None:
            a = m.setdefault("abilities", {}).setdefault("overall", {})
            if a.get("score") != bench["aa"]:
                a["score"] = bench["aa"]
                a["src"] = f"AA Index {asof or 'auto'}"
                changed = True
        # 逻辑 = GPQA
        if bench.get("gpqa") is not None:
            a = m.setdefault("abilities", {}).setdefault("logic", {})
            if a.get("score") != bench["gpqa"]:
                a["score"] = bench["gpqa"]
                a["src"] = f"GPQA {asof or 'auto'}"
                changed = True

        # 上下文窗口
        if pm.get("ctx"):
            if m.get("ctx") != pm["ctx"]:
                m["ctx"] = pm["ctx"]
                changed = True

        # 模态
        if pm.get("modality"):
            if m.get("modality") != pm["modality"]:
                m["modality"] = pm["modality"]
                changed = True

        if changed:
            updated += 1
            print(f"  [UPD] {m['name']} 已刷新（价格/综合/逻辑/上下文/模态）")

    # 汇率
    if fx:
        data["_meta"]["fx_usd_cny"] = round(fx, 6)
        if fx_date:
            data["_meta"]["fx_date"] = fx_date

    # 记录刷新时间
    data["_meta"]["models_refreshed"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    if asof:
        data["_meta"]["source_price"] = f"AI API Index prices.json (CC BY 4.0) — aiapiindex.com, asOf {asof}"

    with open(mp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] models.json 更新完成，{updated} 个模型刷新")


if __name__ == "__main__":
    main()
