# OmniResearch Agent

> ⚠️ **Alpha v1.0.0** — 适用于研究和学习，不建议直接用于生产环境。

Multi-Agent Research Platform with DAG Workflow, RAG Memory, and Tool Routing.

## Features

- **Multi-Agent System** — Planner, Research, Coding, Verify, Reflection
- **DAG Workflow Engine** — Dependency-based parallel execution
- **RAG Memory** — FAISS + sentence-transformers, learns from experience
- **Tool Router** — LLM-powered tool selection (Web/GitHub/PDF/RAG)
- **Auto-Fix Loop** — Code → Execute → Fail → Reflect → Retry
- **Event Bus** — Decoupled logging, dashboard, WebSocket
- **SQLite Persistence** — Tasks, workflows, memories survive restart
- **Multi-Provider LLM** — OpenAI, Gemini, DeepSeek, Ollama
- **Real-time Dashboard** — WebSocket logs, metrics, trace
- **Observability** — Trace stream, metrics, agent performance

## Architecture

```
User Task
    │
    ▼
PlannerAgent (LLM plan)
    │
    ▼
┌─────────────────────────────────────┐
│  DAGExecutor                        │
│  ┌──────────────┐                   │
│  │ AgentRegistry │                   │
│  │  ├─research   │→ ToolRouter      │
│  │  ├─coding     │→ PythonRuntime   │
│  │  ├─verify     │→ LLM Evaluate    │
│  │  └─reflection │→ Learning Memory │
│  └──────────────┘                   │
│  ExecutionContext (shared state)    │
│  EventBus (observers)               │
└─────────────────────────────────────┘
    │
    ▼
SQLite ← Logger, Dashboard, WebSocket
```

## Quick Start

```bash
# Clone
git clone https://github.com/anabcamd123-hash/OmniResearch-Agent.git
cd OmniResearch-Agent

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd dashboard && python3 -m http.server 5500
```

## Docker

```bash
docker compose up --build
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/health/full` | GET | Full system check |
| `/task` | POST | Submit research task |
| `/dashboard` | GET | Runtime metrics |
| `/metrics` | GET | Token/call/retry stats |
| `/trace` | GET | Execution event stream |
| `/history` | GET | Task history |
| `/tasks` | GET | DB task records |
| `/memory` | GET | Agent memories |
| `/upload-pdf` | POST | Upload PDF for RAG |
| `/ws/logs` | WebSocket | Live log stream |

## LLM Providers

```env
# OpenAI
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Ollama (local, free)
MODEL_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# DeepSeek
MODEL_PROVIDER=deepseek
DEEPSEEK_API_KEY=...
```

## Tech Stack

- **Backend**: FastAPI, asyncio, SQLAlchemy
- **LLM**: OpenAI / Gemini / DeepSeek / Ollama
- **Database**: SQLite (async via aiosqlite)
- **RAG**: FAISS + sentence-transformers
- **Search**: DuckDuckGo + GitHub API
- **Frontend**: Vanilla JS + Mermaid
- **Container**: Docker Compose

## Roadmap

- [x] Multi-Agent System
- [x] DAG Workflow Engine
- [x] RAG Memory with FAISS
- [x] Tool Router (LLM-powered)
- [x] Auto-Fix Loop
- [x] Event Bus Architecture
- [x] SQLite Persistence
- [x] Multi-Provider LLM
- [x] Ollama Support
- [x] Observability (Trace/Metrics)
- [x] Docker Compose
- [x] Health Checks
- [ ] MCP Integration
- [ ] PostgreSQL Support
- [ ] Auth & Multi-tenancy

## License

MIT
