# PROGRESS — AI 情报站网页

> 状态：**✅ 已部署上线（GitHub Pages）+ 自动更新闭环**
> URL：https://tanjinrong21-ux.github.io/ai-model-radar/ ｜ repo: tanjinrong21-ux/ai-model-radar
> 更新时间：2026-09-09 07:15 (UTC+8)

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

## 自动更新机制（GitHub Actions，每周云端自动，不依赖电脑开机）
- `.github/workflows/update.yml`：每周日 22:00 UTC（周一 06:00 北京时间）自动触发，也可手动 workflow_dispatch
- 云端链路（ubuntu runner）：
  1. `fetch_models.py`：拉 aiapiindex prices.json（价格/AA综合/GPQA逻辑/上下文/模态）+ open.er-api 汇率 → 刷新已有模型 + **自动发现新模型**（白名单厂商 × flagship/mid，未收录的自动新增，标注「自动收录·待复核」）
  2. `fetch_github.py --build`：GITHUB_TOKEN 并发查 65 repo 星数 → build.py 合成 data.js
  3. `git commit + push`（GITHUB_TOKEN，permissions: contents: write）→ GitHub Pages 自动重建
- 已实测：workflow run 34551321225 success；Actions 于 2026-09-13 自动跑过一周更新（commit 777dac9）
- 本地 cron（原 9486dc2d94fc）已删除，避免与 Actions 双 push 冲突

## 遗留 / 待办
- **数据待 Tommy 实测校准**：PPT/HTML·视觉·语音三个"实践评级"维度的分数是预估，需 Tommy 真实使用后校准
- **手动维护字段**：编程分（SWE-bench，来自 DataLearner）、访问方式、官网链接——这些 fetch_models.py 不自动刷新，需手动维护

## 给 cron 兜底任务的说明
本文件若标注「全部完工」，cron 任务（job dc3981206ea4，2026-09-08 20:00）应直接结束，无需续做。
