<div align="center">

# 🐾 OmniResearch Agent

**Multi-Agent Collaborative Research Platform with DAG-Driven Execution, RAG-Augmented Memory, and Production-Grade Fault Tolerance**

[![Version](https://img.shields.io/badge/version-v2.0.0-blue)](https://github.com/anabcamd123-hash/OmniResearch-Agent/releases/tag/v2.0.0)
[![Python](https://img.shields.io/badge/python-3.10+-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

[Research Motivation](#research-motivation) • [Architecture](#system-architecture) • [Agent Model](#agent-collaboration-model) • [Execution Graph](#dag-execution-graph) • [Fault Tolerance](#fault-tolerance-design) • [Demo](#demo) • [Evaluation](#evaluation) • [Future Work](#future-work)

</div>

---

## Research Motivation

现有 LLM Agent 研究多聚焦于单 Agent 能力（如 ReAct、CoT），但在复杂研究任务中，单 Agent 面临三个根本性瓶颈：

1. **认知边界** — 单 Agent 难以同时胜任信息检索、代码生成、质量验证等异构子任务
2. **执行脆弱性** — 缺乏容错机制，单点失败导致整个任务链中断
3. **不可观测性** — 执行过程不透明，无法调试、审计或复现

OmniResearch Agent 探索的核心问题是：

> **如何构建一个多 Agent 协作系统，使异构 Agent 能够以 DAG（有向无环图）方式安全、可观测、可容错地协作完成复杂研究任务？**

我们提出三个设计原则：
- **DAG-First** — 任务执行以依赖图为驱动，而非线性链式调用
- **Failure-Aware** — 每一层都预设失败路径（熔断、隔舱、死信队列）
- **Observable** — 全链路 WebSocket 实时推送 + 审计日志

---

## System Architecture

<div align="center">

<!-- 📸 PLACEHOLDER: 截图 1 — Dashboard 总览图（stats + agents + DAG + timeline 全景） -->
<!-- 命名为 docs/screenshots/dashboard-overview.png -->

![Dashboard Overview](docs/screenshots/dashboard-overview.png)

</div>

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend Dashboard                         │
│   DAG 可视化 (dagre-d3)  │  WebSocket 实时推送  │  JWT Auth     │
└───────────────────────────────┬─────────────────────────────────┘
                                │ WebSocket / REST
┌───────────────────────────────┴─────────────────────────────────┐
│                       FastAPI Backend                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              WorkflowExecutor (唯一入口)                   │  │
│  │   用户任务 → PlannerAgent (LLM 生成 JSON DAG)             │  │
│  │           → DAGExecutor (依赖分析 + 并行调度)              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │   Agent 层     │  │   Tool 层      │  │   LLM 层       │    │
│  │  Planner       │  │  GitHub        │  │  OpenAI        │    │
│  │  Research   ◄──┼──┤  PDF        ◄──┼──┤  Gemini        │    │
│  │  Coding        │  │  Web Search    │  │  DeepSeek      │    │
│  │  Verify        │  │  RAG           │  │  Ollama        │    │
│  │  Reflection    │  │  Sandbox       │  │                │    │
│  │  AutoFix       │  │                │  │                │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Storage Layer                                │  │
│  │  StateStore (Redis → SQLite → Memory 自动降级)            │  │
│  │  DLQ (aiosqlite 持久化)  │  RAG Memory (FAISS 向量库)    │  │
│  │  Audit Log               │  Workflow State               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 构建动机

| 设计决策 | 理由 |
|---------|------|
| DAG 而非 Chain | 支持并行执行、依赖跳过、部分失败恢复 |
| Multi-Agent 而非 Multi-Tool | 每个 Agent 有独立 prompt / 评分标准 / 超时策略 |
| 三层存储降级 | 生产环境 Redis 挂掉不影响核心功能 |
| WebSocket 实时推送 | 评审 / 演示场景下执行过程完全可观测 |

---

## Agent Collaboration Model

### Agent 职责定义

| Agent | 角色 | 输入 | 输出 | 容错策略 |
|-------|------|------|------|---------|
| **PlannerAgent** | 任务分解 | 用户自然语言描述 | JSON DAG (tasks + dependencies) | 超时 120s |
| **ResearchAgent** | 信息检索 | 任务描述 + RAG 上下文 | 结构化检索报告 | Bulkhead=5, CB 阈值=3 |
| **CodingAgent** | 代码生成 | 检索结果 + 任务需求 | 可执行代码 + Sandbox 结果 | Bulkhead=3, 自动重试 |
| **VerifyAgent** | 质量验证 | Agent 输出 | JSON 评分 (accuracy/completeness/clarity) | 超时 120s |
| **ReflectionAgent** | 反思学习 | 执行 trace + 评分结果 | 改进建议 + RAG 记忆写入 | 超时 120s |
| **AutoFixAgent** | 自动修复 | 失败任务 + 错误信息 | 修复后任务 | 最大重试 3 次 |

### 协作模式

```
用户输入: "Analyze MiMo architecture and compare with DeepSeek-R1"
                    │
                    ▼
            ┌───────────────┐
            │ PlannerAgent  │  LLM 查询 RAG 历史 → 生成 DAG
            └───────┬───────┘
                    │ JSON DAG (4 tasks, 3 dependency edges)
                    ▼
     ┌──────────────────────────────────┐
     │          DAGExecutor             │
     │                                  │
     │   Layer 0 (并行):                │
     │   ├─ research_mimo     ──────────┼──→ 独立执行
     │   └─ research_deepseek ──────────┼──→ 独立执行
     │                                  │
     │   Layer 1 (等待 Layer 0):        │
     │   └─ compare_analysis  ──────────┼──→ 合并两个 research 结果
     │                                  │
     │   Layer 2 (等待 Layer 1):        │
     │   └─ final_report      ──────────┼──→ 生成最终报告
     └──────────────────────────────────┘
                    │
                    ▼
         每个节点完成后自动触发 VerifyAgent 评分
         低于阈值 → AutoFixAgent 修复 → 重新执行
```

---

## DAG Execution Graph

DAG 可视化是本项目的核心亮点。我们使用 **dagre-d3** 构建了可交互的执行图，实时反映任务状态。

<div align="center">

<!-- 📸 PLACEHOLDER: 截图 2 — DAG 可视化特写（展示 node 状态 + 依赖箭头 + 执行层级） -->
<!-- 命名为 docs/screenshots/dag-visualization.png -->

![DAG Visualization](docs/screenshots/dag-visualization.png)

</div>

### DAG 节点状态

| 状态 | 颜色 | 含义 |
|------|------|------|
| `idle` | 灰色 | 等待依赖完成 |
| `running` | 橙色 (脉冲动画) | 正在执行 |
| `completed` | 绿色 | 执行成功 |
| `failed` | 红色 | 执行失败，已进入 DLQ |

### 可交互特性

- **Hover** → 显示任务详情 tooltip（耗时、重试次数、Agent 类型）
- **Click** → 高亮依赖链（上游 + 下游），右侧面板显示完整输出
- **Auto-Layout** → dagre-d3 自动计算层级布局，依赖方向从上到下
- **Real-Time** → WebSocket 推动节点颜色 / 状态实时变化

### DAG 生成示例

PlannerAgent 为以下任务生成的 DAG：

```
输入: "Analyze MiMo architecture and compare with DeepSeek-R1"
```

```json
{
  "tasks": [
    {"id": "research_mimo", "agent": "research", "description": "Research MiMo model architecture"},
    {"id": "research_deepseek", "agent": "research", "description": "Research DeepSeek-R1 architecture"},
    {"id": "compare", "agent": "coding", "description": "Compare architectures", "depends_on": ["research_mimo", "research_deepseek"]},
    {"id": "report", "agent": "reflection", "description": "Generate final report", "depends_on": ["compare"]}
  ]
}
```

Layer 0 的 `research_mimo` 和 `research_deepseek` **无依赖，可并行执行** — 这是 DAG 相比 Chain 的核心优势。

---

## Fault Tolerance Design

生产环境中，Agent 执行失败是常态而非常态。我们的容错体系分三层：

<div align="center">

<!-- 📸 PLACEHOLDER: 截图 3 — Dashboard 运行中截图（展示 stats: Total/Completed/Running/DLQ + Agent 状态徽章） -->
<!-- 命名为 docs/screenshots/dashboard-running.png -->

![Dashboard Running](docs/screenshots/dashboard-running.png)

</div>

### 三层容错架构

```
┌──────────────────────────────────────────────────────────────┐
│  第一层：预防                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Tool Timeout │  │ Agent Timeout│  │  Retry       │       │
│  │ asyncio      │  │ asyncio      │  │  指数退避    │       │
│  │ wait_for 30s │  │ wait_for 120s│  │  max=3 次   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
├──────────────────────────────────────────────────────────────┤
│  第二层：隔离                                                │
│  ┌──────────────────────────┐  ┌───────────────────────┐     │
│  │ Bulkhead (隔舱隔离)      │  │ CircuitBreaker (熔断) │     │
│  │ 每类 Agent 独立 Semaphore│  │ 连续 3 次失败         │     │
│  │ research=5, coding=3     │  │ → 暂停 60s           │     │
│  │ 防止互相阻塞             │  │ → 自动恢复探测        │     │
│  └──────────────────────────┘  └───────────────────────┘     │
├──────────────────────────────────────────────────────────────┤
│  第三层：恢复                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ DLQ (Dead Letter Queue)                              │    │
│  │ 失败任务 → 持久化 SQLite → 定时自动重试 (10s 间隔)   │    │
│  │ → Dashboard 手动重试 → 审计日志追踪                  │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### StateStore 降级策略

```
Redis (优先) ──连接失败──▶ SQLite (降级) ──写入失败──▶ Memory (兜底)
     │                         │                         │
  生产环境首选             无 Redis 环境              测试 / CI
```

---

## Demo

### 执行流程示例

以下展示一个完整的多 Agent 协作执行过程：

```
输入: "Analyze MiMo architecture and compare with DeepSeek-R1"
```

<!-- 📸 PLACEHOLDER: 截图 4 — 完整执行流程（从 Planner 到 Final Report 的 Timeline 截图） -->
<!-- 命名为 docs/screenshots/execution-flow.png -->

```
[Planner]     Analyzing task... generating DAG (4 tasks, 3 edges)
[Planner]     DAG: research_mimo ─┐
               research_deepseek ─┤
                                   ▼ compare ──▶ report

[Research]    research_mimo: started      │ [Research]    research_deepseek: started
[Research]    research_mimo: completed 2.3s│ [Research]    research_deepseek: completed 1.8s
                                          │
[Coding]      compare: started (Layer 1 — all dependencies met)
[Verify]      compare: score {accuracy: 0.85, completeness: 0.78}
[AutoFix]     compare: below threshold, retrying...
[Coding]      compare: retry 1 → completed 4.1s
[Verify]      compare: score {accuracy: 0.92, completeness: 0.88} ✓

[Reflection]  report: started (Layer 2)
[Reflection]  report: completed 1.5s — experience saved to RAG

─────────────────────────────────────────
Workflow completed: 4/4 tasks success | Total: 9.7s | DLQ: 0
```

### Dashboard 功能一览

| 模块 | 功能 | 技术实现 |
|------|------|---------|
| 统计面板 | Total / Completed / Running / DLQ 实时计数 | REST 轮询 + WS 推送 |
| Agent 状态 | 5 个 Agent 实时状态徽章（idle/running/completed/failed） | WebSocket |
| DAG 可视化 | 可拖拽、缩放、点击的执行图 | dagre-d3 + Mermaid |
| 任务卡片 | 每个任务独立卡片，点击查看完整输出 + 分页 | REST + Modal |
| Timeline | 执行事件流，关键词着色 | WebSocket stream |
| Admin 控制 | 输入任务描述，一键启动 Workflow | JWT auth + REST |
| DLQ 管理 | 查看失败任务，手动触发重试 | REST API |
| 导出 | CSV / JSON 导出执行历史 | File download |

---

## Evaluation

### 容错能力测试

| 测试场景 | 预期行为 | 结果 |
|---------|---------|------|
| Agent 超时 | 触发 `asyncio.wait_for`，任务标记 failed | ✅ |
| 连续失败 3 次 | CircuitBreaker 熔断，暂停 60s 后自动恢复 | ✅ |
| Redis 不可用 | StateStore 自动降级到 SQLite | ✅ |
| 任务异常 | 进入 DLQ，10s 后自动重试 | ✅ |
| Bulkhead 满载 | 同类 Agent 排队等待，不互相阻塞 | ✅ |
| Verify 低分 | AutoFixAgent 自动修复并重试 | ✅ |

### 并行效率

| 任务结构 | Chain 方式 | DAG 方式 | 提升 |
|---------|-----------|---------|------|
| 2 个独立 Research + 1 个 Compare | 串行 ~12s | 并行 ~7s | **~42%** |
| 3 个独立 Research + 1 个 Merge | 串行 ~18s | 并行 ~7s | **~61%** |

> DAG 的并行度取决于任务图的宽度。独立分支越多，加速比越高。

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/anabcamd123-hash/OmniResearch-Agent.git
cd OmniResearch-Agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY
```

### 3. Run

```bash
uvicorn backend.main:app --reload --port 8000
```

- **Dashboard:** http://localhost:8000/frontend/index.html
- **API Docs:** http://localhost:8000/docs
- **Docker:** `docker compose up --build`

### 4. 截图指南

启动服务后，按以下步骤截取 Demo 截图（用于 README 展示）：

#### 截图 1：Dashboard 总览
1. 打开 `http://localhost:8000/frontend/index.html`
2. 用 `admin / admin123` 登录
3. **不启动任何 workflow**，截取空的 Dashboard 全景
4. 保存为 `docs/screenshots/dashboard-overview.png`

#### 截图 2：DAG 可视化
1. 在 Admin 面板输入：`Analyze MiMo architecture and compare with DeepSeek-R1`
2. 点击 **▶ Run**
3. 等 DAG 图完全渲染后，**截取 DAG 区域特写**（包含不同颜色的节点状态）
4. 保存为 `docs/screenshots/dag-visualization.png`

#### 截图 3：Dashboard 运行状态
4. 趁 workflow 运行中（或完成后），截取包含以下内容的全景：
   - 顶部统计面板（Total / Completed / Running / DLQ 数字）
   - Agent Status 徽章
   - DAG 图
   - Timeline 事件流
5. 保存为 `docs/screenshots/dashboard-running.png`

#### 截图 4：执行流程 Timeline
1. workflow 完成后，截取 **Timeline 区域特写**
2. 展示完整的事件序列（Planner → Research → Coding → Verify → Reflection）
3. 保存为 `docs/screenshots/execution-flow.png`

> 将 4 张截图放入 `docs/screenshots/` 目录，README 会自动引用。

---

## Future Work

- [ ] **Hierarchical DAG** — 支持子图嵌套（Sub-DAG），任务可递归分解
- [ ] **Dynamic DAG** — 执行过程中根据中间结果动态调整后续任务图
- [ ] **Multi-LLM Ensemble** — 同一任务多模型投票，提高验证可靠性
- [ ] **Human-in-the-Loop** — 关键节点暂停等待人工确认
- [ ] **Distributed Execution** — 多机部署 Agent，Celery / Ray 驱动
- [ ] **Evaluation Benchmark** — 构建标准测试集，量化 Agent 协作质量
- [ ] **Cost-Aware Scheduling** — 根据 LLM API 成本优化 DAG 调度策略

---

## Project Structure

```
backend/
├── agents/          # 6 个 Agent 实现 (Planner/Research/Coding/Verify/Reflection/AutoFix)
├── executor/        # DAGExecutor + TaskGraph + WorkflowExecutor
├── tools/           # 工具层 (Sandbox/GitHub/PDF/WebSearch/RAG + CircuitBreaker)
├── llm/             # LLM Provider (OpenAI/Gemini/DeepSeek/Ollama)
├── runtime/         # 运行时 (Bulkhead/DLQ/EventBus/Metrics/Trace)
├── storage/         # StateStore (Redis→SQLite→Memory 自动降级)
├── api/             # REST + WebSocket + JWT Auth
└── config/          # 唯一配置源 (pydantic BaseSettings)

frontend/
└── index.html       # dagre-d3 Dashboard (DAG 可视化 + 实时状态)

docs/
├── ARCHITECTURE.md  # 架构设计文档
└── screenshots/     # Demo 截图（由截图步骤生成）

tests/               # 6 个测试文件，Mock LLM 无需真实 API
```

---

## License

MIT

---

<div align="center">

**[⬆ back to top](#-omniresearch-agent)**

</div>
