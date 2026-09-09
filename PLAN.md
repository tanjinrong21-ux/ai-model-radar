# PLAN — AI 情报站（AI Models / Skills / Tools Radar）

> 版本：v0.1（草案，待 Tommy 确认）
> 日期：2026-09-07 23:55 (UTC+8)
> 状态：⏳ 等待 Tommy 评审

---

## 1. 需求（Tommy 原始需求要点）

一个公开网页，让访客（含 Tommy 自己）及时掌握：
1. **大模型能力榜**：国内外最新 AI 模型综合能力排名
2. **7 个能力维度可筛选**：综合 / 编程开发 / 逻辑 / PPT&HTML / 视觉 / 语音多模态 / 百万 token 成本(¥)
3. **访问方式颜色区分**：需翻墙 vs 不需翻墙
4. 点模型 → 链到官网，获得使用帮助
5. **自动更新**
6. **Skill 榜**：链接 skill 排名与简介（GitHub 星数等公开榜），知道最新 skill
7. **工具榜**：热门 AI 工具排名 + 简介 + 获取链接（Tommy 需要时让路飞去学）
8. **风格**：AI 科幻风，参考海贼王悬赏令风格

**最终目的**：及时知道最新大模型能力 → 在合适时机优化本地 Hermes 的模型与工作方式。

## 2. 调研结论（2026-09-07 实测）

### 2.1 权威模型数据源（2026年9月格局）
| 数据源 | 覆盖 | 获取方式 | 可用性 |
|---|---|---|---|
| **Artificial Analysis 智能指数** | 10项基准综合（编程/数学/科学/推理/Agent） | 免费 API（1000次/日，需注册key）或官网页面 | 需注册 key |
| **LMArena Elo**（原 Chatbot Arena） | 用户盲测偏好 | **HuggingFace 数据集 `lmarena-ai/leaderboard-dataset`**（CC BY 4.0，无需 key） | ✅ 直下 |
| **SWE-bench Verified / LiveCodeBench** | 编程能力 | DataLearner 聚合榜等 | ✅ 可抓 |
| **DataLearner 中文聚合榜**（datalearner.com/leaderboards） | 综合+数学+编程+Agent，中英双语 | 网页（有数据更新日期） | ✅ |
| **aiapiindex.com** | 73模型/17供应商/9基准 + 价格 | 网页 | ✅ 参考 |
| 厂商官方定价页 | 百万 token 成本（USD） | 官方页面 | ✅ 半自动 |

**2026-09 前哨观察**（用于初始数据与验证基准）：国际前沿 Anthropic（Claude Fable 5/5.1、Opus 5）、OpenAI（GPT-5.6/5.5）、Google（Gemini 3.x）领跑综合；国内 DeepSeek-V4、Kimi K3/K2.5、Qwen 3.6+、GLM 5.x、MiniMax、豆包 Seed 2.x 位居第一梯队。→ **初始数据集以多源交叉为准，每一条标注来源与日期，不靠单一搜索快照。**

### 2.2 Skill 数据源（GitHub 星数）
| 源 | 说明 |
|---|---|
| GitHub Search API（gh 已认证 → 5000次/小时） | 按 `claude-skill / awesome-agent-skills / skill` 等关键词查星数 |
| yuxiaopeng/Github-Ranking-AI（自动更新榜） | 综合类星数榜（AI_Agents/Claude 分类含 ECC、hermes-agent、superpowers 等） |
| linny006/trending-claude-skills（15分钟自动更新） | 新趋势 skill 发现 |

### 2.3 工具数据源
GitHub API 星数 + 人工精选清单（含获取方式/官网）+ 可选 GitHub Trending 抓取。

### 2.4 现状：真实、完整、诚实
- **没有「单一权威综合榜」**——AA Index（客观基准）与 LMArena（主观偏好）双榜并列是行业标准做法。
- **PPT/HTML、语音质量无统一公开基准** → 设计为「实践评级」字段，初始由 Tommy/路飞基于真实使用标注依据，每期数据标「最近复核日」。不伪装成 benchmark。
- **成本人民币**：按当日汇率换算，页面标注汇率与日期。

## 3. 架构设计

```
D:\AI land\AI工具网页\            ← 本目录 = git repo（远端 GitHub）
├── index.html                    ← 单页应用：三大板块（模型榜/技能榜/工具榜）
├── assets/
│   ├── css/style.css             ← AI科幻 + 悬赏令风格
│   ├── js/app.js                 ← 渲染 + 7维筛选 + tab 切换
│   └── js/data.js                ← ★由 build.py 生成的数据文件（JSONP 式）
├── data/
│   ├── models.json               ← 源数据：模型主数据（人工+自动合成）
│   ├── skills.json               ← 源数据：skill 清单（含 github repo）
│   ├── tools.json                ← 源数据：工具清单
│   └── meta.json                 ← 数据更新时间、汇率、来源说明
├── scripts/
│   ├── fetch_github.py           ← GitHub API 拉星数 → 写回 skills/tools
│   ├── fetch_models.py           ← （可选）HF LMArena 数据集 → 模型基准
│   ├── build.py                  ← 校验 + 合成 → data.js + meta 时间戳
│   └── check_links.py            ← 链接有效性检查
├── .github/workflows/            ← 自动更新（云端 Actions，不依赖本机）
│   └── update.yml                ← 每日 fetch_github + build + deploy
└── PLAN.md / QA 报告             ← 过程留痕
```

### 3.1 数据模型（核心 schema）
**模型条目 models.json：**
```json
{
  "id": "deepseek-v4-pro",
  "name": "DeepSeek-V4-Pro",
  "vendor": "深度求索",
  "country": "CN",
  "release": "2026-06",
  "access": "direct",              // direct=国内直连 | vpn=需翻墙 | 开源可本地跑另标 badge
  "homepage": "https://platform.deepseek.com/",
  "docs": "https://api-docs.deepseek.com/",
  "abilities": {
    "overall":   {"score": 90, "src": "AA Index 2026-09-02 | LMArena Elo 2026-09-01"},
    "coding":    {"score": 88, "src": "SWE-bench Verified 2026-09"},
    "logic":     {"score": 87, "src": "..."},
    "ppt_html":  {"score": 8,  "grade": "实践评级", "src": "Tommy实测 2026-09", "note": "HTML单文件PPT交付已验证"},
    "vision":    {"score": 75, "src": "..."},
    "audio":     {"score": 70, "src": "..."}
  },
  "price_usd_in": 0.28,            // 每百万token输入USD
  "price_usd_out": 2.19,           // 每百万token输出USD
  "price_cny": {...}               // build 时按汇率换算（输入/输出，单位 ¥/百万token）
}
```
分数统一 0-100 归一化，**每条带 src（来源+日期）**，无来源不显示分数（显示"—"）。

### 3.2 自动更新设计（务实混合，诚实标注）
| 层级 | 频率 | 内容 | 自动化程度 |
|---|---|---|---|
| GitHub 星数（skills/tools） | **每日 06:00 UTC**（cron 或 Actions，取决于是否部署） | fetch_github.py → build | 100% 自动 |
| 模型 benchmark 分 | **每周日 06:00 UTC** | fetch_models.py 拉 LMArena HF 数据集 + AA 页面解析 | 90% 自动（需路飞 web 复核新增模型） |
| 实践评级（ppt_html/audio/vision 质量、访问方式、官网） | 事件驱动 | 路飞在对话中随模型发布/实测更新 | 人工/半自动，页面标注「最近复核」 |
| 汇率 | 每次 build 自动 | 拉取公开汇率（如 open.er-api） | 100% 自动 |

> **v1 本地预览阶段的自动更新**：脚本完整可跑（手动触发或 Tommy 电脑上 cron），因无远端托管，GitHub Actions 云端更新在 v2 公开部署时再启用。

每次 build 自动更新 `meta.json`：数据生成 UTC 时间 → 页面显示「数据更新于 …」。→ **诚实机制：页面永远显示数据时间，用户知道新鲜度。**

### 3.3 视觉设计（AI科幻 + 海贼王悬赏令）
- 深空黑蓝渐变 + 霓虹青/紫光效 + 细网格/扫描线（科技感）
- **模型卡片 = 悬赏令（WANTED 风格）**：模型名大字、厂商、"Bounty" 位放能力分徽章、每能力维度小字标签
- Top 榜前 3 给「皇冠/海贼旗」视觉特效；翻墙状态 = 🟢 绿(直连) / 🔴 红(需翻墙) 双色体系
- 移动端自适应（Tommy 手机查看）
- 图表：能力雷达或横向条，轻量（纯 CSS/SVG，不引外部库保加载速度）

### 3.4 部署
**当前阶段（v1）：本地/内网预览** — 浏览器直接打开 index.html 即可用（数据全部本地 data.js 内嵌，无跨域）。脚本 build.py 每次生成 data.js 后刷新即可看到更新。
**后续可选（v2，Tommy 决定后再做）**：GitHub Pages 公开（沿用 iso9001-news 已验证模式），或内网服务器托管。

## 4. 执行阶段（Do）

| 阶段 | 内容 | 产出 | 复杂度 |
|---|---|---|---|
| **P1 数据脚手架** | schema + 首批数据：**15-20 个模型**（国际8-10+国内8-10）、**10-15 个 skill repo**、**10-15 个工具**；多源交叉核对，每条带来源日期 | data/*.json 全量填充 | 复杂 |
| **P2 页面构建** | index.html + style.css（悬赏令卡片+科幻风）+ app.js（7维筛选+排序+tab+搜索） | 本地可打开的单页站 | 复杂 |
| **P3 自动更新+部署** | scripts/*.py 测试跑通 → git repo + GH Pages → Actions workflow 实跑一次 | 公开 URL + 自动更新链路 | 复杂 |
| **P4 QA+验收** | 乌索普三维验证 → 修复循环 → Tommy 验收 | QA 报告 + 放行 | — |

## 5. 验证条件（Check 清单 — 功能目标）

| # | 功能目标（用户可感知） | 谁验 | 何时验 | 不通过处理 |
|---|---|---|---|---|
| 1 | 桌面/手机浏览器直接打开本地 index.html，模型榜默认按综合能力排序，显示排名/分数/访问颜色/官网 | Tommy + 路飞 | P2 后即可初验，P3 终验 | 回退修复 |
| 2 | 切换 7 个能力维度（综合/编程/逻辑/PPT-HTML/视觉/语音/成本¥），榜单实时重排；成本列单位人民币并标注汇率 | Tommy | P3 后 | 回退 P2 |
| 3 | 需翻墙模型显示红色系、国内直连显示绿色系，视觉上明显可辨 | Tommy | P3 后 | 回退 P2 |
| 4 | 点击任意模型 → 新标签打开其官网/文档页（抽样 5 个 curl 验 200） | 路飞 | P3 后 | 修链接 |
| 5 | 页面脚注显示「数据更新于 <UTC 时间>」，与实际 build 脚本运行时间一致（真实跑通一次 fetch+build） | 路飞 | P3 完成后 | 修脚本 |
| 6 | Skill 榜显示真实 GitHub 星数（fetch 脚本实跑，与 gh api 查询值一致）；含简介与 repo 链接 | 路飞 | P3 后 | 修脚本 |
| 7 | 工具榜含名称/简介/获取方式/官网链接；每个工具可点开 | 路飞 | P3 后 | 修数据 |
| 8 | 数据真实性抽查：随机抽 3 个模型，分数与页面标注来源可核对一致（无编造分数） | 乌索普 | QA 阶段 | 退回修正 |
| 9 | 页面无 Markdown 泄漏、无 JS 报错、移动端不破版、风格符合「科幻+悬赏令」 | 乌索普 | QA 阶段 | 退回修正 |
| 10 | 任意能力分数无来源 → 显示"—"而非编造值；页面有数据免责/来源声明 | 乌索普 | QA 阶段 | 退回修正 |

## 6. 决策点（待 Tommy 拍板，逐个确认）

**Q1. 发布与可见性**（已决议 ✅）：**先本地/内网预览**，公开部署押后到 v2。

**Q2. 数据范围与深度**（已决议 ✅）：**首批 15-20 个主流模型**（国内一线：DeepSeek/Kimi/Qwen/GLM/豆包/MiniMax；国际：Claude/GPT/Gemini/Grok），模型卡附**成本对比**（输入/输出 ¥/百万token）与**上下文窗口**列。

**Q3. 视觉风格偏向**（已决议 ✅）：**悬赏令味道更浓**——通缉令边框/蜡封感/榜一海贼王风格大卡，配合科幻深色底。其余科幻元素（扫描线/霓虹）做背景层，不喧宾夺主。

## 7. 风险与对策
| 风险 | 对策 |
|---|---|
| 搜索结果含不可靠榜单站（如 swfte/oxzhan） | 初始数据多源交叉，标注一手来源；不用单一搜索快照 |
| 模型更新极快，分数过期 | 页面显示数据时间；每周自动刷 benchmark |
| HF 数据集结构变化 | fetch 脚本容错 + 失败告警（Actions 失败通知） |
| 无 key 限流（GitHub 60/h 无 token） | gh 已认证自动带 token（5000/h） |
| 版权 | LMArena HF 数据集 CC BY 4.0，页面署名来源 |
| 「实践评级」主观 | 明确标注为实践评级非 benchmark，附实测说明与日期 |

## 8. 复盘预留（Act）
完成时输出：成功经验 / 失败经验 / 未解之谜；如流程性问题则固化进 skill。
