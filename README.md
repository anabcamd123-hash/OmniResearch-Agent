<div align="center">

# 🐾 OmniResearch Agent

**Multi-Agent Research Platform with DAG Workflow, RAG Memory & Production-Grade Fault Tolerance**

[![Version](https://img.shields.io/badge/version-v2.0.0-blue)](https://github.com/anabcamd123-hash/OmniResearch-Agent/releases/tag/v2.0.0)
[![Python](https://img.shields.io/badge/python-3.10+-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API](#-api) • [Dashboard](#-dashboard) • [Docs](#-documentation)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 Multi-Agent System
- **PlannerAgent** — LLM 驱动的 JSON DAG 规划
- **ResearchAgent** — 信息检索 + RAG 上下文
- **CodingAgent** — 代码生成 + 自动重试
- **VerifyAgent** — 结构化 JSON 评分
- **ReflectionAgent** — 质量分析 + 学习记忆
- **AutoFixAgent** — 自动修复闭环

</td>
<td width="50%">

### 🏗️ Production Architecture
- **DAG Executor** — 基于依赖的并行调度
- **Circuit Breaker** — 连续失败自动熔断
- **Bulkhead** — 按类型隔离并发
- **DLQ** — 失败任务持久化 + 自动重试
- **StateStore** — Redis → SQLite → Memory 自动降级
- **Audit Log** — 全链路操作审计

</td>
</tr>
<tr>
<td>

### 🔧 Tool System
- **Sandbox** — 统一执行入口（超时 + 隔舱 + 审计）
- **GitHub Analyzer** — 仓库分析
- **PDF Parser** — 文档解析
- **Web Search** — DuckDuckGo 搜索
- **RAG Tool** — 向量检索历史知识
- **Python Sandbox** — 子进程隔离执行

</td>
<td>

### 📊 Dashboard
- **dagre-d3** — 可拖拽 DAG 可视化
- **WebSocket** — 实时状态推送
- **Agent 状态圆点** — 每个 Agent 实时状态
- **进度条 + 时长** — 节点动态样式
- **依赖高亮** — 点击节点高亮依赖链
- **DLQ 管理** — 查看 / 手动重试

</td>
</tr>
</table>

---

## 🏛️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend Dashboard                     │
│  dagre-d3 DAG │ WebSocket │ Admin Controls │ Auth        │
└────────────────────────┬─────────────────────────────────┘
                         │ WebSocket / REST
┌────────────────────────┴─────────────────────────────────┐
│                    FastAPI Backend                        │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ WorkflowExecutor (唯一入口)                          │ │
│  │   → PlannerAgent (JSON DAG)                         │ │
│  │   → DAGExecutor                                     │ │
│  │       ├─ TaskGraph (依赖分析)                        │ │
│  │       ├─ CircuitBreaker (熔断)                       │ │
│  │       ├─ Bulkhead (并发隔离)                         │ │
│  │       └─ asyncio.gather (并行执行)                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Agents     │  │    Tools     │  │    LLM       │   │
│  │  Research    │  │  GitHub      │  │  OpenAI      │   │
│  │  Coding      │──│  PDF         │──│  Gemini      │   │
│  │  Verify      │  │  Web Search  │  │  DeepSeek    │   │
│  │  Reflection  │  │  RAG         │  │  Ollama      │   │
│  │  AutoFix     │  │  Sandbox     │  │              │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Storage Layer                                       │ │
│  │  StateStore (Redis → SQLite → Memory)               │ │
│  │  DLQ (aiosqlite)  │  Memory (学习经验)              │ │
│  │  Audit Log        │  Workflow State                 │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Task Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    OmniResearch Agent Workflow                  │
└─────────────────────────────────────────────────────────────────┘

用户输入任务描述
       │
       ▼
┌──────────────┐
│ PlannerAgent │  ← 任务分解 + DAG 生成
│   (规划者)    │     查询 RAG 历史知识 → LLM 生成执行计划
└──────┬───────┘
       │
       ▼  输出 Task 列表（含依赖关系）
┌──────────────────────────────────────────────────────────────┐
│                      DAGExecutor                             │
│                 (DAG 任务图执行器)                            │
│                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │research │───▶│ coding  │───▶│ verify  │                  │
│  │  检索   │    │  编码   │    │  验证   │                  │
│  └─────────┘    └─────────┘    └────┬────┘                  │
│                                     │                        │
│                                     ▼                        │
│                              ┌─────────────┐                 │
│                              │ reflection  │                 │
│                              │  反思改进   │                 │
│                              └─────────────┘                 │
│                                                              │
│  ⚡ 并发: asyncio.gather (按依赖层级并行)                     │
│  🛡️ 隔离: Bulkhead (每类 Agent 独立信号量)                    │
│  🔌 容错: CircuitBreaker + DLQ (失败自动重试)                 │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                      Agent 职责详情                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  🔍 ResearchAgent (检索)                                     │
│     ├─ RAG 查询历史知识库                                    │
│     ├─ Web 搜索 / GitHub 分析 / PDF 解析                     │
│     └─ LLM 总结信息                                          │
│                                                              │
│  💻 CodingAgent (编码)                                       │
│     ├─ 基于检索结果生成代码                                   │
│     ├─ Python Sandbox 安全执行                               │
│     └─ 失败自动重试 (指数退避)                                │
│                                                              │
│  ✅ VerifyAgent (验证)                                       │
│     ├─ 结构化 JSON 评分 (accuracy/completeness/clarity)      │
│     └─ 阈值判断 (pass/fail)                                   │
│                                                              │
│  🔄 ReflectionAgent (反思)                                   │
│     ├─ 分析执行过程 + 质量评估                                │
│     ├─ 提出改进建议                                          │
│     └─ 保存经验到 RAG 记忆库 (学习)                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                      运行时保护层                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  🛡️ Bulkhead (隔舱隔离)                                      │
│     每类 Agent 独立 Semaphore，防止互相阻塞                   │
│                                                              │
│  ⚡ CircuitBreaker (熔断器)                                   │
│     连续失败 3 次 → 暂停该 Agent 60s → 自动恢复               │
│                                                              │
│  📥 DLQ (死信队列)                                           │
│     失败任务持久化 SQLite → 定时自动重试 → 手动干预           │
│                                                              │
│  📊 RuntimeState (实时状态)                                  │
│     WebSocket 推送 → Agent 状态 / Timeline / 任务输出         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                      前端 Dashboard                          │
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │DAG 可视化│  │Agent 状态│  │任务卡片 │  │Timeline │        │
│  │ dagre-d3 │  │ 实时徽章 │  │点击查看 │  │ 事件流  │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│                                                              │
│  优化模块 (可独立开关):                                       │
│  Sort / SearchHistory / VirtualScroll / MultiTask            │
│  WebSocket / ProgressChart / ExportPDF                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/anabcamd123-hash/OmniResearch-Agent.git
cd OmniResearch-Agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```dotenv
# Required
OPENAI_API_KEY=sk-...

# Optional (defaults shown)
MODEL_PROVIDER=openai
OPENAI_TIMEOUT=60
MAX_RETRY=3
BULKHEAD_RESEARCH=5
BULKHEAD_CODING=3
CIRCUIT_BREAKER_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT=60
```

### 3. Run

```bash
uvicorn backend.main:app --reload --port 8000
```

Dashboard: [http://localhost:8000/frontend/index.html](http://localhost:8000/frontend/index.html)

API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Docker

```bash
docker compose up --build
```

---

## 📡 API

### Core

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/task` | POST | - | 提交研究任务 |
| `/executor/submit` | POST | JWT | 提交工作流 |
| `/executor/status/{id}` | GET | JWT | 查询任务状态 |

### Agent & Workflow

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/workflow/{id}` | GET | Workflow 详情 + per-task 状态 |
| `/workflows/running` | GET | 运行中的 workflows |
| `/workflow/{id}/resume` | POST | 手动恢复 |
| `/dashboard` | GET | 运行时指标 |
| `/health/breakers` | GET | 熔断器状态 |
| `/health/tools` | GET | 工具审计统计 |

### Auth & Security

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/token` | POST | JWT 登录 (admin/admin123) |
| `/auth/me` | GET | 当前用户信息 |
| `/tasks/retry/{id}` | POST | 重试任务 (admin only) |

### DLQ & Export

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dlq` | GET | 查看失败任务 |
| `/dlq/retry` | POST | 手动重试一个 |
| `/dlq/clear` | DELETE | 清空 DLQ |
| `/export/history/csv` | GET | 导出 CSV (需登录) |
| `/export/history/json` | GET | 导出 JSON (需登录) |
| `/audit/logs` | GET | 审计日志 (admin) |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://host/ws` | 实时状态推送 + 接收命令 |

---

## 🖥️ Dashboard

<div align="center">

```
┌─ Login ─────────────────────────────────────────┐
│ [admin] [****] [Login]                           │
├──────────────────────────────────────────────────┤
│ Total │ Completed │ Running │ DLQ                │
├──────────┬───────────────────────────────────────┤
│ Agents   │ DAG Workflow (dagre-d3)               │
│ badges   │ ┌─────────────────────────────┐       │
│          │ │ research_1 ──→ coding_1     │       │
│          │ │      │              │        │       │
│          │ │      ▼              ▼        │       │
│          │ │ verify_1 ──→ reflection_1   │       │
│          │ └─────────────────────────────┘       │
│          │ [hover tooltip] [click → deps]        │
├──────────┴───────────────────────────────────────┤
│ Admin: [task description...] [▶ Start Workflow]  │
│ WS Log: [Planner] DAG: 4 tasks                   │
│         [Research] research_1: completed 1.2s     │
├──────────────────────────────────────────────────┤
│ Audit Log │ DLQ Tasks │ Workflow History          │
└──────────────────────────────────────────────────┘
```

</div>

### Dashboard 功能

| 功能 | 说明 |
|------|------|
| DAG 可视化 | dagre-d3，支持拖拽 + 缩放 |
| 节点交互 | hover 显示 tooltip，点击高亮依赖链 + 详情面板 |
| Agent 状态 | 5 个圆点实时显示 research/coding/verify/reflection/autofix 状态 |
| 进度条 | 每个节点底部显示进度 + 执行时长 |
| 折叠/展开 | 有子任务的节点可折叠 |
| Admin 控制 | 输入任务描述，一键启动 workflow |
| DLQ 管理 | 查看失败任务，手动重试 |
| 实时日志 | WebSocket 推送，关键词着色 |

---

## 🔧 Configuration

All settings in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key |
| `MODEL_PROVIDER` | `openai` | LLM provider |
| `OPENAI_TIMEOUT` | `60` | OpenAI 超时 (秒) |
| `MAX_RETRY` | `3` | 任务最大重试次数 |
| `BULKHEAD_RESEARCH` | `5` | research 并发数 |
| `BULKHEAD_CODING` | `3` | coding 并发数 |
| `CIRCUIT_BREAKER_THRESHOLD` | `3` | 熔断阈值 |
| `CIRCUIT_BREAKER_TIMEOUT` | `60` | 熔断恢复时间 (秒) |
| `AGENT_TIMEOUT` | `120` | Agent 执行超时 |
| `DLQ_RETRY_INTERVAL` | `10` | DLQ 自动重试间隔 (秒) |
| `REDIS_URL` | `redis://localhost:6379` | Redis 连接 |
| `DATABASE_URL` | `sqlite+aiosqlite:///data/app.db` | 主数据库 |

---

## 📁 Project Structure

```
backend/
├── agents/           # Multi-Agent 层
│   ├── registry.py         # Factory 注册表
│   ├── planner_agent.py    # JSON DAG 规划
│   ├── research_agent.py   # 信息检索
│   ├── coding_agent.py     # 代码生成 + 自动重试
│   ├── verify_agent.py     # JSON 评分
│   ├── reflection_agent.py # 质量分析
│   └── autofix_agent.py    # 自动修复
│
├── executor/         # 执行器层
│   ├── workflow_executor.py   # 唯一入口
│   ├── dag_executor.py        # DAG 调度 + Bulkhead + CB + DLQ
│   ├── task_graph.py          # 依赖图
│   └── retry.py               # 指数退避重试
│
├── tools/            # 工具层
│   ├── sandbox.py             # 统一执行（超时 + 隔舱 + 审计）
│   ├── router.py              # LLM 工具选择
│   ├── bulkhead.py            # 并发隔离
│   └── circuit_breaker.py     # 熔断器
│
├── llm/              # LLM Provider 层
│   ├── openai_provider.py
│   ├── gemini_provider.py
│   └── deepseek_provider.py
│
├── storage/          # 存储层
│   ├── state_factory.py       # 自动降级：Redis → SQLite → Memory
│   ├── sqlite_state.py
│   ├── redis_state.py
│   └── mem_state.py
│
├── config/
│   └── settings.py            # 唯一配置源 (pydantic BaseSettings)
│
├── api/              # REST + WebSocket
│   ├── routes_auth.py         # JWT 认证
│   ├── routes_executor.py     # 任务提交
│   ├── routes_dlq.py          # DLQ 管理
│   └── routes_dashboard_ws.py # WebSocket
│
frontend/
└── index.html                 # dagre-3 Dashboard

docs/
└── ARCHITECTURE.md            # 架构文档 + Mermaid 图

tests/
├── conftest.py                # Mock LLM
├── test_bulkhead.py
├── test_dlq.py
├── test_retry.py
├── test_scheduler.py
└── test_state_store.py
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_bulkhead.py -v

# With coverage
pytest tests/ --cov=backend --cov-report=term-missing
```

Tests use Mock LLM — no real API calls needed.

---

## 🛡️ Fault Tolerance

| Layer | Mechanism | Config |
|-------|-----------|--------|
| Tool Timeout | `asyncio.wait_for` | `TOOL_TIMEOUT_DEFAULT=30` |
| Agent Timeout | `asyncio.wait_for` | `AGENT_TIMEOUT=120` |
| Circuit Breaker | Per-agent-type, auto recovery | `CIRCUIT_BREAKER_THRESHOLD=3` |
| Bulkhead | `Semaphore` per type | `BULKHEAD_*` |
| DLQ | SQLite persistent | Auto retry every `DLQ_RETRY_INTERVAL` |
| Retry | Exponential backoff | `MAX_RETRY=3` |
| StateStore | Redis → SQLite → Memory | Auto fallback |

---

## 📈 Changelog

### v2.0.0 (2026-05-22)

- 🏗️ **Architecture consolidation** — Single entry point, single config, single DLQ
- ⚡ **DAGExecutor simplified** — TaskGraph + gather (removed Queue/Worker)
- 🔧 **Bulkhead** — Context manager pattern
- 🗄️ **StateStore** — Redis → SQLite → Memory auto-fallback
- 🔐 **JWT Auth** — admin/viewer roles
- 📊 **Dashboard upgrade** — dagre-d3, drag, zoom, dependency highlight
- 🧪 **Tests** — 6 test files with Mock LLM
- 📖 **Architecture docs** — Mermaid diagrams

### v1.0.0

- Multi-Agent system with DAG workflow
- RAG memory with FAISS
- Tool routing with LLM selection
- SQLite persistence
- Real-time WebSocket dashboard

---

## 📄 License

MIT

---

<div align="center">

**[⬆ back to top](#-omniresearch-agent)**

</div>
