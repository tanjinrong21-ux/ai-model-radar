#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_models.py — 自动刷新 + 自动发现模型数据。
数据源：aiapiindex.com/prices.json（CC BY 4.0 公开数据）+ open.er-api.com 汇率。
功能：
  1. 刷新已有模型：价格 / 综合(AA) / 逻辑(GPQA) / 上下文 / 模态 / 汇率
  2. 自动发现新模型：白名单厂商 × (flagship|mid) 中，models.json 尚未收录的 → 自动新增
本地与 GitHub Actions 均可运行（纯 urllib）。
人工字段（access/homepage/docs/实践评级/编程分）保持不动，自动新增模型标注「自动收录·待复核」。
"""
import json
import os
import re
import sys
import urllib.request
import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")

PRICES_URL = "https://aiapiindex.com/prices.json"
FX_URL = "https://open.er-api.com/v6/latest/USD"

# models.json 的 name -> prices.json 的 name（处理命名差异）
NAME_ALIAS = {
    "文心 ERNIE 5.1": "ERNIE 5.1",
}

# 白名单厂商 -> (国家, 访问方式, 官网)
VENDOR_META = {
    "OpenAI": ("US", "vpn", "https://openai.com/"),
    "Anthropic": ("US", "vpn", "https://www.anthropic.com/claude"),
    "Google": ("US", "vpn", "https://gemini.google.com/"),
    "xAI": ("US", "vpn", "https://x.ai/"),
    "Meta": ("US", "vpn", "https://ai.meta.com/"),
    "DeepSeek": ("CN", "direct", "https://platform.deepseek.com/"),
    "Alibaba Qwen": ("CN", "direct", "https://tongyi.aliyun.com/"),
    "Moonshot AI": ("CN", "direct", "https://www.moonshot.cn/"),
    "Zhipu AI (Z.ai)": ("CN", "direct", "https://www.z.ai/"),
    "MiniMax": ("CN", "direct", "https://www.minimaxi.com/"),
    "Baidu": ("CN", "direct", "https://yiyan.baidu.com/"),
}


def http_get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "ai-model-radar/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _slug(name):
    s = name.lower().replace(" ", "-").replace(".", "")
    return re.sub(r"[^a-z0-9\-]", "", s)


def main():
    print("=== fetch_models.py — 模型数据刷新 + 自动发现 ===")

    try:
        prices = http_get_json(PRICES_URL)
        llm = prices.get("llm", [])
        asof = prices.get("asOf", {}).get("llm", "?")
        print(f"[OK] prices.json 拉取成功，{len(llm)} 个模型，asOf={asof}")
    except Exception as e:
        print(f"[WARN] prices.json 拉取失败，跳过: {e}")
        llm, asof = [], "?"

    fx = None
    try:
        fx = http_get_json(FX_URL).get("rates", {}).get("CNY")
        print(f"[OK] 汇率拉取成功：1 USD = {fx} CNY")
    except Exception as e:
        print(f"[WARN] 汇率拉取失败，保留原值: {e}")

    mp = os.path.join(DATA_DIR, "models.json")
    with open(mp, encoding="utf-8") as f:
        data = json.load(f)

    prices_by_name = {p.get("name"): p for p in llm if p.get("name")}

    # ---- 1. 刷新已有模型 ----
    updated = 0
    for m in data["models"]:
        pm = prices_by_name.get(NAME_ALIAS.get(m["name"], m["name"]))
        if not pm:
            continue
        changed = False
        if pm.get("inPrice") is not None and pm.get("outPrice") is not None:
            new_price = {"in": pm["inPrice"], "out": pm["outPrice"]}
            if m.get("price") != new_price:
                m["price"] = new_price
                changed = True
        bench = pm.get("bench") or {}
        if bench.get("aa") is not None:
            a = m.setdefault("abilities", {}).setdefault("overall", {})
            if a.get("score") != bench["aa"]:
                a["score"] = bench["aa"]
                a["src"] = f"AA Index {asof}"
                changed = True
        if bench.get("gpqa") is not None:
            a = m.setdefault("abilities", {}).setdefault("logic", {})
            if a.get("score") != bench["gpqa"]:
                a["score"] = bench["gpqa"]
                a["src"] = f"GPQA {asof}"
                changed = True
        if pm.get("ctx") and m.get("ctx") != pm["ctx"]:
            m["ctx"] = pm["ctx"]
            changed = True
        if pm.get("modality") and m.get("modality") != pm["modality"]:
            m["modality"] = pm["modality"]
            changed = True
        if changed:
            updated += 1
    print(f"[OK] 已有模型刷新：{updated} 个")

    # ---- 2. 自动发现新模型 ----
    existing = set()
    for m in data["models"]:
        existing.add(m["name"])
        if m["name"] in NAME_ALIAS:
            existing.add(NAME_ALIAS[m["name"]])

    added = []
    for p in llm:
        prov = p.get("provider")
        if prov not in VENDOR_META:
            continue
        if p.get("tier") not in ("flagship", "mid"):
            continue
        if p.get("name") in existing:
            continue
        country, access, homepage = VENDOR_META[prov]
        b = p.get("bench") or {}
        data["models"].append({
            "id": _slug(p["name"]),
            "name": p["name"],
            "vendor": prov,
            "country": country,
            "access": access,
            "open": p.get("license") != "prop",
            "homepage": homepage,
            "docs": homepage,
            "release": p.get("released") or "",
            "ctx": p.get("ctx") or 0,
            "modality": p.get("modality") or "T",
            "price": {"in": p.get("inPrice"), "out": p.get("outPrice")},
            "note": "自动收录·待复核",
            "abilities": {
                "overall": {"score": b.get("aa"), "src": f"AA Index {asof}" if b.get("aa") is not None else "无 AA 公开数据"},
                "coding": {"score": None, "src": "SWE-bench 无公开数据"},
                "logic": {"score": b.get("gpqa"), "src": f"GPQA {asof}" if b.get("gpqa") is not None else "无公开数据"},
                "ppt_html": {"score": None, "src": "待复核"},
                "vision": {"score": None, "src": "待复核"},
                "audio": {"score": None, "src": "待复核"},
            },
        })
        existing.add(p["name"])
        added.append(p["name"])

    if added:
        print(f"[OK] 自动收录 {len(added)} 个新模型：")
        for n in added:
            print(f"   + {n}")
    else:
        print("[OK] 无新模型需收录")

    # ---- 3. 元数据 ----
    if fx:
        data["_meta"]["fx_usd_cny"] = round(fx, 6)
        data["_meta"]["fx_date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    data["_meta"]["models_refreshed"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    if llm:
        data["_meta"]["source_price"] = f"AI API Index prices.json (CC BY 4.0) — aiapiindex.com, asOf {asof}"

    with open(mp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] models.json 完成：共 {len(data['models'])} 个模型")


if __name__ == "__main__":
    main()
