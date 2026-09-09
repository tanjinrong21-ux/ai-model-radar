#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_data.py — 生成 skills.json 与 tools.json（含场景分类）。
星数为 2026-09-08 gh api 实查。8 场景 skill + 5 分类工具，每类 5 个。"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

# ---- Skill 数据（8 场景 × 5）----
# (id, repo, name, stars, lang, scene, desc, get)
SKILLS = [
    # agent 框架
    ("superpowers","obra/superpowers","Superpowers",282740,"Shell","agent","Agentic skills 框架 + 软件开发方法论，社区最火的 skills 集合（规划/测试/调试等可复用模块）。","git clone 后按 skill 安装，或作 Claude Code 插件引入"),
    ("ecc","affaan-m/ECC","ECC",252491,"JavaScript","agent","Agent harness 性能优化系统，提供 skills/instincts/memory/security 与 research-first 开发。","npm 安装或 git clone，作为 agent 的 harness 层挂载"),
    ("hermes-agent","NousResearch/hermes-agent","Hermes Agent",242955,"Python","agent","「与你一起成长的 agent」，Tommy 正在用的本机框架，支持 skills/记忆/cron/多模型/多平台。","pip install hermes-agent，已在本机运行"),
    ("karpathy-skills","multica-ai/andrej-karpathy-skills","Karpathy Skills",210833,"None","agent","单个 CLAUDE.md 文件提升 Claude Code 行为，源自 Andrej Karpathy 的工作流。","复制 CLAUDE.md 到项目根目录即可"),
    ("claude-cookbook","anthropics/claude-cookbook","Claude Cookbook",52555,"Jupyter Notebook","agent","Anthropic 官方 Claude 用法食谱集，覆盖 agent/工具调用/多模态等 notebook 样例。","clone 仓库按 notebook 跑示例"),
    # 编码开发
    ("codex","openai/codex","Codex CLI",122498,"TypeScript","coding","OpenAI 轻量编码 agent，跑在终端，支持多步代码生成与执行。","npm install @openai/codex 或官方 CLI"),
    ("cline","cline/cline","Cline",67624,"TypeScript","coding","自主编码 agent，SDK/IDE 插件/CLI 三形态，带 Plan/Act 与浏览器能力。","VS Code 插件市场安装 Cline"),
    ("gpt-engineer","gpt-engineer-org/gpt-engineer","GPT Engineer",55102,"Python","coding","CLI 代码生成平台，自然语言描述 → 生成/迭代代码库。","pip install gpt-engineer"),
    ("aider","Aider-AI/aider","Aider",48811,"Python","coding","终端 AI 结对编程，Git 原生（自动 commit/diff），支持多模型与 repo map。","pip install aider-install && aider-install"),
    ("continue","continuedev/continue","Continue",35834,"TypeScript","coding","开源编码 agent，IDE 内嵌，支持多模型与代码库问答。","VS Code/JetBrains 插件安装 Continue"),
    # 文档处理
    ("anthropic-skills","anthropics/skills","Anthropic Skills",174994,"Python","docs","Anthropic 官方 Agent Skills：docx/pdf/pptx/xlsx 文档处理 skill 权威来源。","clone 后复制 skill 目录到 agent skills"),
    ("docling","docling-project/docling","Docling",66167,"Python","docs","IBM 文档解析，把 PDF/Word 等转成 LLM 友好的结构化格式。","pip install docling"),
    ("marker","datalab-to/Marker","Marker",39599,"Python","docs","把 PDF 快速转 markdown + JSON，识别公式/表格/图片，高保真。","pip install marker-pdf"),
    ("unstructured","Unstructured-IO/unstructured","Unstructured",15409,"Python","docs","文档转结构化数据的开源工具，支持 PDF/PPT/HTML/邮件等多种格式。","pip install unstructured"),
    ("jina-reader","jina-ai/reader","Jina Reader",11964,"Python","docs","任意 URL 转 LLM 友好输入（Reader API），网页转 markdown 免爬虫。","r.jina.ai 前缀 URL 即可，或 jina 云 API"),
    # 工具集成
    ("mcp-servers","modelcontextprotocol/servers","MCP Servers",90138,"TypeScript","tools","Model Context Protocol 官方参考服务器集（文件/Git/数据库/搜索等）。","npx/pip 安装对应 server，配置进 agent MCP 列表"),
    ("langgraph","langchain-ai/langgraph","LangGraph",41263,"Python","tools","构建有状态、可恢复的多 agent 工作流的编排框架。","pip install langgraph"),
    ("copilotkit","CopilotKit/CopilotKit","CopilotKit",37251,"TypeScript","tools","Agent 与生成式 UI 的前端栈，React 组件 + AG-UI 协议。","npm install @copilotkit/react-core"),
    ("composio","ComposioHQ/composio","Composio",30090,"TypeScript","tools","为 AI agent 提供 1000+ 工具集成（Gmail/Sheets/GitHub 等）+ 工具搜索。","pip/npm 安装，composio add <tool> 接入"),
    ("openai-agents","openai/openai-agents-python","OpenAI Agents",29270,"Python","tools","OpenAI 官方多 agent 框架，轻量、支持 handoff/工具/护栏。","pip install openai-agents"),
    # 内容采集
    ("firecrawl","firecrawl/firecrawl","Firecrawl",177919,"TypeScript","research","网页搜索/抓取 API，任意网页转干净 Markdown，供 agent 读取。","云 API 或自托管，pip/npm 安装 firecrawl"),
    ("browser-use","browser-use/browser-use","Browser Use",113230,"Python","research","让 AI agent 真正操作浏览器，自动化网页任务，登录态可持久。","pip install browser-use"),
    ("crawl4ai","unclecode/crawl4ai","Crawl4AI",81964,"Python","research","开源 LLM 友好的网页爬虫，专门为 AI 提取网页数据优化。","pip install crawl4ai"),
    ("scrapegraphai","ScrapeGraphAI/Scrapegraph-ai","ScrapeGraphAI",30727,"Python","research","基于 LLM 的爬虫，用图结构描述抓取逻辑，自动解析网页。","pip install scrapegraphai"),
    ("gpt-researcher","assafelovic/gpt-researcher","GPT Researcher",29355,"Python","research","自主研究 agent，自动联网搜索、聚合、生成深度研究报告。","pip install gpt-researcher"),
    # 课件演示
    ("revealjs","hakimel/reveal.js","reveal.js",72279,"JavaScript","slides","HTML 演示框架，网页幻灯片事实标准，横向翻页/动画/导出 PDF。","npm 安装或 CDN 引入，Markdown 驱动"),
    ("slidev","slidevjs/slidev","Slidev",48464,"TypeScript","slides","面向开发者的演示，Markdown 驱动 + Vue 组件，代码高亮，导出 PDF/PPTX。","npm init slidev"),
    ("impress","impress/impress.js","impress.js",38169,"JavaScript","slides","基于 CSS 3D 变换的演示框架，空间感强，做炫酷幻灯片。","CDN 引入或 npm 安装"),
    ("remark","gnab/remark","Remark",13001,"JavaScript","slides","浏览器内 Markdown 驱动的幻灯片，轻量极简。","CDN 引入，Markdown 写幻灯片"),
    ("marp","marp-team/marp","Marp",12468,"TypeScript","slides","Markdown 演示生态（CLI/VS Code 插件），md 转 PDF/PPT/HTML。","VS Code 装 Marp 插件或 npx @marp-team/marp-cli"),
    # 设计可视化
    ("excalidraw","excalidraw/excalidraw","Excalidraw",131416,"TypeScript","design","手绘风格虚拟白板，生成手绘感图表/流程图，JSON 可编程。","在线 excalidraw.com 或 npm 包，导出 PNG/SVG"),
    ("mermaid","mermaid-js/mermaid","Mermaid",90165,"TypeScript","design","文本生成流程图/时序图/甘特图/类图，Markdown 原生支持。","CDN/npm 引入，代码块即渲染"),
    ("d2","terrastruct/d2","D2",25318,"Go","design","现代图表脚本语言，文本声明式生成架构图/流程图。","brew/npm 安装 d2，d2 file.d2 生成 SVG"),
    ("plantuml","plantuml/plantuml","PlantUML",13305,"Java","design","文本生成 UML 图（类图/时序图/用例图），老牌稳定。","下载 jar 或在线 plantuml.com"),
    ("drawio","jgraph/drawio","draw.io",7994,"JavaScript","design","开源的客户端流程图编辑器，可导出 SVG/PNG/XML。","在线 app.diagrams.net 或桌面端"),
    # 知识库
    ("mem0","mem0ai/mem0","Mem0",64913,"Python","knowledge","AI agent 的记忆层，drop-in 提供长期记忆与个性化。","pip install mem0ai"),
    ("quivr","QuivrHQ/quivr","Quivr",39497,"Python","knowledge","RAG「第二大脑」，把文档/链接接入私有知识库并对话。","docker 自托管或 quivr.com 云版"),
    ("onyx","onyx-dot-app/onyx","Onyx",31978,"Python","knowledge","开源 AI 平台，企业级 RAG + AI Chat，连接内部知识源。","docker compose 自托管"),
    ("graphiti","getzep/graphiti","Graphiti",30697,"Python","knowledge","为 AI agent 构建实时知识图谱，动态关联实体与关系。","pip install graphiti-core"),
    ("haystack","deepset-ai/haystack","Haystack",26449,"Python","knowledge","开源 AI 编排框架，构建 RAG/agent/检索管线。","pip install haystack-ai"),
]

# ---- 工具数据（5 分类 × 5）----
# (id, repo, name, stars, lang, cat, desc, url, get)
TOOLS = [
    # 本地部署
    ("ollama","ollama/ollama","Ollama",180386,"Go","local","本地跑大模型的事实标准，一条命令下载运行 Kimi/GLM/DeepSeek/Qwen 等开源模型。","https://ollama.com/","官网下载安装包，ollama pull <模型>"),
    ("llama-cpp","ggerganov/llama.cpp","llama.cpp",127505,"C++","local","C/C++ LLM 推理引擎，GGUF 模型在 CPU/GPU 上跑，量化灵活。","https://github.com/ggerganov/llama.cpp","git clone 编译或下载 release"),
    ("vllm","vllm-project/vllm","vLLM",91170,"Python","local","高吞吐低内存 LLM 推理服务引擎，生产部署开源模型的标准。","https://docs.vllm.ai/","pip install vllm，vllm serve <model>"),
    ("localai","mudler/LocalAI","LocalAI",48958,"Go","local","无 GPU 也能跑 LLM/视觉/语音/图像，OpenAI 兼容 API 本地替代。","https://localai.io/","二进制或 docker 部署"),
    ("sglang","sgl-project/sglang","SGLang",35647,"Python","local","高性能推理服务框架，RadixAttention 加速，支持多模态与 agent。","https://sglang.ai/","pip install sglang"),
    # 应用平台
    ("n8n","n8n-io/n8n","n8n",203640,"TypeScript","platform","Fair-code 工作流自动化平台，原生 AI 能力，可自托管。","https://n8n.io/","npm/docker 自托管或 n8n.cloud"),
    ("dify","langgenius/dify","Dify",154731,"TypeScript","platform","可视化构建 Agentic workflow/RAG 管线的一站式平台。","https://dify.ai/","docker compose 自托管或云版"),
    ("langflow","langflow-ai/langflow","Langflow",154461,"TypeScript","platform","可视化拖拽构建 LLM 应用与 agent 流程。","https://www.langflow.org/","pip install langflow 或 docker"),
    ("anything-llm","Mintplex-Labs/anything-llm","AnythingLLM",65785,"JavaScript","platform","本地优先的全栈 AI 应用，接文档做 RAG，桌面端一键装。","https://anythingllm.com/","桌面安装包或 docker"),
    ("flowise","FlowiseAI/Flowise","Flowise",55433,"TypeScript","platform","可视化构建 AI agent 与工作流，低代码拖拽。","https://flowiseai.com/","npm install -g flowise 或 docker"),
    # Agent 平台
    ("autogpt","Significant-Gravitas/AutoGPT","AutoGPT",187178,"Python","agent","让 AI 自主完成多步任务的经典 agent 平台，可视化构建器。","https://agpt.co/","pip 安装或 agpt.co 云版"),
    ("openhands","All-Hands-AI/OpenHands","OpenHands",86438,"TypeScript","agent","AI 驱动的软件开发 agent，自主写代码/跑测试/改 bug。","https://www.all-hands.dev/","docker 启动或云版"),
    ("metagpt","geekan/MetaGPT","MetaGPT",70267,"Python","agent","多 agent 框架，模拟软件公司角色协作，一句话生成项目。","https://github.com/geekan/MetaGPT","pip install metagpt"),
    ("chatdev","OpenBMB/ChatDev","ChatDev",34237,"Python","agent","多 agent 软件开发框架，用自然语言驱动多个角色协作开发。","https://github.com/OpenBMB/ChatDev","git clone 后跑示例"),
    ("swe-agent","princeton-nlp/SWE-agent","SWE-Agent",20284,"Python","agent","输入 GitHub issue，agent 自动修 bug 并提交 PR。","https://swe-agent.com/","pip install swe-agent"),
    # 界面客户端
    ("open-webui","open-webui/open-webui","Open WebUI",151222,"Python","ui","用户友好的 AI 界面，对接 Ollama/OpenAI API，带 RAG/多用户/语音。","https://openwebui.com/","pip install open-webui 或 docker"),
    ("awesome-llm-apps","Shubhamsaboo/awesome-llm-apps","Awesome LLM Apps",136506,"Python","ui","100+ AI Agent/Agent Skills/RAG 应用免费开源合集，找样板首选。","https://github.com/Shubhamsaboo/awesome-llm-apps","clone 仓库按目录运行"),
    ("lobehub","lobehub/lobehub","LobeHub",82291,"TypeScript","ui","「首席 Agent 运营官」，编排 agent 团队 7×24 工作，LobeChat 生态。","https://lobehub.com/","npm/docker 部署 LobeChat"),
    ("librechat","danny-avila/LibreChat","LibreChat",42926,"TypeScript","ui","增强版 ChatGPT 克隆，支持多模型/MCP/RAG/多用户，可自托管。","https://www.librechat.ai/","docker 或 npm 部署"),
    ("astrbot","AstrBotDevs/AstrBot","AstrBot",40160,"Python","ui","AI agent 助手框架，整合多 IM 平台（微信/QQ/钉钉）与多 LLM。","https://astrbot.app/","pip install astrbot"),
    # 框架 SDK
    ("langchain","langchain-ai/langchain","LangChain",145873,"Python","sdk","Agent 工程平台，构建 LLM 应用的框架事实标准。","https://www.langchain.com/","pip install langchain"),
    ("autogen","microsoft/autogen","AutoGen",60873,"Python","sdk","微软多 agent 编程框架，定义角色对话协作解决任务。","https://microsoft.github.io/autogen/","pip install autogen-agentchat"),
    ("llama-index","run-llama/llama_index","LlamaIndex",52072,"Python","sdk","文档 agent 与 OCR 平台，构建 RAG/知识问答的框架。","https://www.llamaindex.ai/","pip install llama-index"),
    ("semantic-kernel","microsoft/semantic-kernel","Semantic Kernel",28546,"C#","sdk","微软 LLM SDK，把 LLM 技术快速集成进 C#/Python/Java 应用。","https://learn.microsoft.com/semantic-kernel/","pip install semantic-kernel"),
    ("composio","ComposioHQ/composio","Composio",30090,"TypeScript","sdk","为 AI agent 提供 1000+ 工具集成与工具搜索，MCP 原生支持。","https://composio.dev/","pip/npm 安装，composio add <tool>"),
]


def main():
    scenes = {"agent":"Agent 框架","coding":"编码开发","docs":"文档处理","tools":"工具集成","research":"内容采集","slides":"课件演示","design":"设计可视化","knowledge":"知识库"}
    tool_cats = {"local":"本地部署","platform":"应用平台","agent":"Agent 平台","ui":"界面客户端","sdk":"框架 SDK"}

    skills_out = {
        "_meta": {
            "source": "GitHub API (gh) 实查 — 2026-09-08",
            "note": "星数为 GitHub 实时 stargazers_count。scene=应用场景分类，每场景 5 个。",
            "scenes": scenes,
        },
        "skills": [
            {"id": s[0], "repo": s[1], "name": s[2], "stars": s[3], "lang": s[4], "scene": s[5],
             "desc": s[6], "url": "https://github.com/" + s[1], "get": s[7]}
            for s in SKILLS
        ],
    }

    tools_out = {
        "_meta": {
            "source": "GitHub API (gh) 实查 — 2026-09-08",
            "note": "星数为 GitHub 实时 stargazers_count。cat=工具分类，每类 5 个。",
            "cats": tool_cats,
        },
        "tools": [
            {"id": t[0], "repo": t[1], "name": t[2], "stars": t[3], "lang": t[4], "cat": t[5],
             "desc": t[6], "url": t[7], "repo_url": "https://github.com/" + t[1], "get": t[8]}
            for t in TOOLS
        ],
    }

    with open(os.path.join(DATA, "skills.json"), "w", encoding="utf-8") as f:
        json.dump(skills_out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "tools.json"), "w", encoding="utf-8") as f:
        json.dump(tools_out, f, ensure_ascii=False, indent=2)

    # 校验每类数量
    from collections import Counter
    sc = Counter(s["scene"] for s in skills_out["skills"])
    tc = Counter(t["cat"] for t in tools_out["tools"])
    print("Skill 总数:", len(skills_out["skills"]), "场景分布:", dict(sc))
    print("Tool 总数:", len(tools_out["tools"]), "分类分布:", dict(tc))
    bad = [k for k,v in sc.items() if v != 5] + ["tool:"+k for k,v in tc.items() if v != 5]
    if bad:
        print("[WARN] 以下分类不是 5 个:", bad)
    else:
        print("[OK] 所有分类均为 5 个")


if __name__ == "__main__":
    main()
