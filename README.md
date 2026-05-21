# OmniResearch Agent

AI Multi-Agent Research Platform

## Features

- Multi-Agent Workflow (Planner → Research → Coding → Verify → Reflection)
- DAG Runtime with dependency-based execution
- Real-time Dashboard (WebSocket + auto-refresh)
- PDF RAG (upload papers, vector search, cited answers)
- GitHub Analyzer (stars, forks, issues)
- Python Runtime (execute generated code)
- Web Search (DuckDuckGo integration)
- Auto-fix Code (LLM sees error, fixes, re-executes)
- Memory Store (Agent context sharing)
- Tool Router (auto-select Web/GitHub/PDF)
- SQLite Persistence (tasks, workflows, logs survive restart)
- Token Tracking (per-agent token usage)
- Mermaid DAG Visualization (auto-generated workflow graphs)
- Multi-Provider LLM (OpenAI / Gemini / DeepSeek)
- Retry System (configurable retries with status tracking)
- Docker Compose (backend + frontend + Redis)

## Architecture

```
User Task
    │
    ▼
PlannerAgent (LLM plan)
    │
    ▼
┌─────────────────────────────────┐
│  DAG Executor                   │
│  ┌───────────┐                  │
│  │ Research   │← Tool Router    │
│  │            │  ├─ Web Search  │
│  │            │  ├─ GitHub      │
│  │            │  └─ PDF RAG     │
│  └─────┬─────┘                  │
│        ▼                        │
│  ┌───────────┐                  │
│  │ Coding     │→ Python Runtime │
│  │            │→ Auto-fix       │
│  └─────┬─────┘                  │
│        ▼                        │
│  ┌───────────┐                  │
│  │ Verify     │← LLM Evaluate   │
│  └─────┬─────┘                  │
│        ▼                        │
│  ┌───────────┐                  │
│  │ Reflection │← LLM Analysis   │
│  └───────────┘                  │
└─────────────────────────────────┘
    │
    ▼
Dashboard + SQLite + Memory
```

## DAG Workflow

```
graph TD
    Research --> Coding
    Coding --> Verify
    Verify --> Reflection
```

## Dashboard

Real-time panels:
- Runtime Metrics (tasks, tokens)
- Agent Status (idle/running/completed)
- DAG Workflow (Mermaid visualization)
- Task History (with duration)
- Agent Timeline (color-coded events)
- Live Logs (WebSocket streaming)

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

# Run backend
uvicorn backend.main:app --reload

# Run frontend (separate terminal)
cd frontend && python3 -m http.server 5500
```

Open: http://127.0.0.1:5500

## Docker

```bash
docker compose up
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/task` | POST | Submit research task |
| `/dashboard` | GET | Runtime metrics |
| `/history` | GET | Task history |
| `/db/tasks` | GET | SQLite task records |
| `/db/workflows` | GET | SQLite workflow records |
| `/upload-pdf` | POST | Upload PDF for RAG |
| `/ws/logs` | WS | Live log stream |

## Tech Stack

- **Backend**: FastAPI, asyncio
- **LLM**: OpenAI / Gemini / DeepSeek (factory pattern)
- **Database**: SQLite + Redis
- **RAG**: FAISS + sentence-transformers
- **Search**: DuckDuckGo + GitHub API
- **Frontend**: Vanilla JS + Mermaid
- **Container**: Docker Compose

## License

MIT
