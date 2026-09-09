# PROGRESS — AI 情报站网页

> 状态：**✅ 全部完工（乌索普 QA 四轮通过，含 8 场景 skill + 5 分类工具）**
> 更新时间：2026-09-08 16:30 (UTC+8)

## 项目概要
本地浏览器可直接打开的单页网页，三大板块：模型能力榜 / Skill 榜 / 工具榜。视觉风格：海贼王悬赏令味浓 + AI 科幻深色底。

## 完成清单

### P1 数据脚手架 ✅
- `data/models.json`：20 个模型（国际 10 + 国内 10），多源交叉：
  - 综合=AA智能指数、编程=SWE-bench、逻辑=GPQA（benchmark 真实分数）
  - 价格=AI API Index prices.json（CC BY 4.0，官方定价）
  - PPT/HTML·视觉·语音=实践评级（预估，标注"待实测校准"）
  - 每维度带 src（来源+日期），无来源=null（页面显示"—"）
- `data/skills.json`：40 个 skills（8 场景 × 5，GitHub 星数实查）
- `data/tools.json`：25 个工具（5 分类 × 5，GitHub 星数实查 + 中文简介 + 获取方式）
- `scripts/gen_data.py`：批量生成 skills/tools 数据（星数硬编码 2026-09-08 实查值）

### P2 页面构建 ✅
- `index.html`：单页三大 tab + 7 维筛选 + 访问方式过滤 + skill 8 场景筛选 + 工具 5 分类筛选
- `assets/css/style.css`：纵列排行榜（悬赏令横向条/排名放大/蜡封/皇冠Top1）+ 科幻深空底
- `assets/js/app.js`：渲染 + 排序 + 筛选逻辑（7 维排序 + 场景/分类过滤均已验证）
- `assets/js/data.js`：build.py 生成（价格人民币换算 + 时间戳）

### P3 自动更新脚本 ✅
- `scripts/build.py`：JSON→data.js 合成 + USD→CNY 换算 + 数据完整性校验
- `scripts/fetch_github.py`：GitHub 星数自动更新（gh api 实查，已实跑验证）
- 数据源文件：`data/prices_raw.json`（aiapiindex）、`data/fx_raw.json`（汇率）

## 运行方式
- **查看页面**：浏览器直接打开 `index.html`（无需服务器）
- **刷新星数 + 重建**：`python scripts/fetch_github.py --build`
- **仅重建**：`python scripts/build.py`

## 验证结果
- ✅ 20 模型渲染正确，按综合能力排序（Claude Fable 5.1 👑 NO.1）
- ✅ 7 维筛选排序正确（编程 Opus 5=96 / 逻辑 GPT-6 Astra=96.1 / 成本 GLM-5.3-Flash 最便宜 / 视觉·语音 Gemini=9）
- ✅ 访问红绿区分（10 直连 / 10 翻墙，绿/红+emoji 三重标识）
- ✅ 人民币换算正确（汇率 1 USD = 6.719397 CNY，2026-09-07）
- ✅ 官网链接可达（Claude/OpenAI 200/403；Grok/Gemini/Meta 直连 URLError 印证"需翻墙"标记正确）
- ✅ 自动更新链路实跑通过（cron 9486dc2d94fc 每日 06:00，last_status=ok）
- ✅ 乌索普 QA 两轮通过（第1轮 3 退回+2 待确认 → 第2轮 5/5 放行）

## 自动更新机制（已上线）
- cron job `9486dc2d94fc`「AI情报站-每日自动更新」，每日 06:00，no_agent 跑 `radar_update.py`
- wrapper：`C:\Users\et_21\AppData\Local\hermes\scripts\radar_update.py` → 项目 `scripts/fetch_github.py --build`
- 链路：fetch_github.py（gh api 拉 21 个 repo 星数）→ 更新 skills/tools.json → build.py 合成 data.js

## 遗留 / 待办
- **v2 可选**：GitHub Pages 公开部署（当前仅本地预览，Tommy 已决议暂缓）
- **v2 可选**：fetch_models.py 从 aiapiindex prices.json 自动刷新模型价格/benchmark（当前模型数据为手动维护 + 每日星数自动刷新）
- **数据待 Tommy 实测校准**：PPT/HTML·视觉·语音三个"实践评级"维度的分数是预估，需 Tommy 真实使用后校准

## 给 cron 兜底任务的说明
本文件若标注「全部完工」，cron 任务（job dc3981206ea4，2026-09-08 20:00）应直接结束，无需续做。
