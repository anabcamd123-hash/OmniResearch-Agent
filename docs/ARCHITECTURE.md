# OmniResearch Agent — 架构文档

## 系统架构图

```mermaid
graph TD
    subgraph Frontend["Frontend Dashboard"]
        FE[dagre-d3 DAG 可视化]
        WS[WebSocket 实时订阅]
        UI[任务操作 / DLQ / 搜索]
    end

    subgraph Backend["Backend (FastAPI)"]
        subgraph API["API Layer"]
            REST[REST API]
            WSEndpoint[WebSocket Endpoint]
            Auth[JWT Auth]
        end

        subgraph Executor["Executor Layer"]
            WorkflowExecutor
            DAGExecutor[DAGExecutor<br/>Queue + Worker + Scheduler]
            TaskQueue[TaskQueue + DLQ]
            Retry[retry_async + CircuitBreaker]
            Checkpoint[CheckpointStore]
        end

        subgraph Agents["Agent Layer"]
            Planner[PlannerAgent<br/>JSON DAG]
            Research[ResearchAgent]
            Coding[CodingAgent<br/>auto retry]
            Verify[VerifyAgent<br/>JSON output]
            Reflection[ReflectionAgent<br/>JSON output]
            AutoFix[AutoFixAgent]
        end

        subgraph LLM["LLM Layer"]
            OpenAI[OpenAI]
            Gemini[Gemini]
            DeepSeek[DeepSeek]
            Ollama[Ollama]
        end

        subgraph Tools["Tool Layer"]
            Sandbox[ToolSandbox<br/>timeout + bulkhead + audit]
            GitHub[GitHub]
            PDF[PDF Parser]
            Web[Web Search]
            RAG[RAG Tool]
        end

        subgraph Storage["Storage Layer"]
            StateRepo[StateRepository<br/>Redis → SQLite → Memory]
            DLQRepo[DLQRepository<br/>SQLite]
            Memory[MemoryRepository]
            SQLAlchemy[(SQLite / PostgreSQL)]
        end

        subgraph Runtime["Runtime"]
            EventBus[EventBus]
            Metrics[Metrics]
            Audit[AuditLog]
            Bulkhead[Bulkhead]
        end
    end

    FE -->|WebSocket| WSEndpoint
    REST --> WorkflowExecutor
    WorkflowExecutor --> Planner
    WorkflowExecutor --> DAGExecutor
    DAGExecutor --> TaskQueue
    TaskQueue --> Retry
    Retry --> Agents
    Agents --> LLM
    Agents --> Tools
    Tools --> Sandbox
    DAGExecutor --> Checkpoint
    DAGExecutor --> DLQRepo
    Agents --> Memory
    Agents --> Audit
    DAGExecutor --> Bulkhead
```

## 任务执行流程

```mermaid
flowchart TD
    A[用户提交任务<br/>POST /task] --> B[WorkflowExecutor]
    B --> C[PlannerAgent<br/>生成 JSON DAG]
    C --> D[DAGExecutor.execute]

    D --> E[DAGScheduler<br/>找 ready tasks]
    E --> F[TaskQueue.put]
    F --> G[Worker × N<br/>并发消费]

    G --> H{CircuitBreaker<br/>tripped?}
    H -->|否| I[Agent.run]
    H -->|是| J[跳过 → DLQ]

    I --> K{成功?}
    K -->|是| L[Checkpoint.save completed]
    K -->|否| M{重试次数<br/>max=2}
    M -->|未耗尽| I
    M -->|耗尽| N[DLQ.push<br/>SQLite 持久化]

    L --> O[WebSocket 推送]
    N --> O

    O --> P[Dashboard 更新<br/>DAG 节点状态]

    P --> Q{还有任务?}
    Q -->|是| E
    Q -->|否| R[Workflow 完成<br/>保存学习模式]
```

## 配置系统

```mermaid
graph LR
    subgraph Config["唯一配置源"]
        Settings[backend/config/settings.py<br/>pydantic BaseSettings]
    end

    subgraph Env[".env"]
        DotEnv[OPENAI_API_KEY<br/>MAX_RETRY=3<br/>BULKHEAD_RESEARCH=5<br/>...]
    end

    DotEnv --> Settings
    Settings --> Executor
    Settings --> Providers
    Settings --> Tools
    Settings --> Bulkhead
```

## 状态降级策略

```mermaid
flowchart TD
    A[build_state_repo] --> B{Redis<br/>可用?}
    B -->|是| C[RedisStateRepository]
    B -->|否| D{SQLite<br/>可用?}
    D -->|是| E[SQLiteStateRepository]
    D -->|否| F[MemStateRepository<br/>兜底]

    C --> G[统一接口<br/>get / set / delete]
    E --> G
    F --> G
```

## 目录结构

```
backend/
├── agents/           # Agent 层
│   ├── registry.py         # Factory 模式注册表
│   ├── planner_agent.py    # JSON DAG 规划
│   ├── research_agent.py
│   ├── coding_agent.py     # 自动重试
│   ├── verify_agent.py     # JSON 输出
│   ├── reflection_agent.py # JSON 输出
│   └── autofix_agent.py
│
├── executor/         # 执行器层
│   ├── workflow_executor.py   # 唯一入口
│   ├── dag_executor.py        # Queue + Worker + Scheduler
│   ├── dag_scheduler.py       # 依赖调度
│   ├── worker.py              # 并发 Worker
│   ├── task_queue.py          # asyncio.Queue + DLQ
│   ├── checkpoint.py          # Redis 状态持久化
│   ├── dlq_worker.py          # 延迟自动重试
│   └── retry.py               # 指数退避重试
│
├── tools/            # 工具层
│   ├── sandbox.py             # 统一执行入口
│   ├── router.py              # 工具选择
│   ├── circuit_breaker.py     # 熔断器
│   └── tool_audit.py          # 调用审计
│
├── llm/              # LLM 层
│   ├── provider_factory.py
│   ├── openai_provider.py
│   ├── gemini_provider.py
│   └── deepseek_provider.py
│
├── runtime/          # 运行时
│   ├── bulkhead.py            # 统一并发控制
│   ├── workflow_state.py      # Redis 运行态
│   └── runtime_state.py       # 全局状态
│
├── storage/          # 存储层
│   ├── state_repository.py    # 抽象接口
│   ├── sqlite_state.py
│   ├── redis_state.py
│   ├── mem_state.py           # 兜底
│   ├── state_factory.py       # 自动降级
│   ├── dlq_repository.py      # SQLite DLQ
│   └── repository.py          # SQLAlchemy CRUD
│
├── config/
│   └── settings.py            # 唯一配置源
│
├── api/
│   ├── routes_task.py
│   ├── routes_executor.py
│   ├── routes_auth.py
│   ├── routes_dlq.py
│   ├── routes_dashboard.py
│   └── routes_dashboard_ws.py
│
frontend/
└── index.html                 # dagre-d3 Dashboard

tests/
├── conftest.py                # Mock LLM
├── test_state_store.py
├── test_dlq.py
├── test_bulkhead.py
├── test_scheduler.py
└── test_retry.py

archive/executor/              # 归档旧文件
```

## 统一入口

```python
# 执行任务
from backend.executor.workflow_executor import WorkflowExecutor
executor = WorkflowExecutor()
result = await executor.execute("Analyze GitHub repo")

# 配置
from backend.config.settings import settings
settings.OPENAI_TIMEOUT  # 60

# 状态存储
from backend.storage.state_factory import build_state_repo
store = await build_state_repo()  # Redis → SQLite → Memory

# 并发控制
from backend.runtime.bulkhead import research_bulkhead
result = await research_bulkhead.run(agent.run(task))

# DLQ
from backend.storage.dlq_repository import DLQRepository
dlq = DLQRepository()
await dlq.add_task("task_id", retries=0)
```
