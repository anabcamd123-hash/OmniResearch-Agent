# OmniResearch Agent — 操作指南

## 快速开始

### 1. 安装

```bash
git clone https://github.com/anabcamd123-hash/OmniResearch-Agent.git
cd OmniResearch-Agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
```

编辑 `.env`，填入 API Key：

```dotenv
OPENAI_API_KEY=sk-your-key-here
MODEL_PROVIDER=openai
```

### 3. 启动

```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. 打开 Dashboard

浏览器访问：`http://localhost:8000/frontend/index.html`

---

## Dashboard 使用

### 登录

- 默认账号：`admin` / `admin123`
- 登录后可启动 Workflow、管理 DLQ

### 提交任务

1. 登录后在 **Start Workflow** 区域输入任务描述
2. 点击 **▶ Run** 或按回车
3. 系统自动执行：Planner → Research → Coding → Verify → Reflection

### 查看状态

| 区域 | 内容 |
|------|------|
| 顶部统计 | Total / Completed / Running / DLQ |
| Agent Status | 每个 Agent 的实时状态 |
| DAG | 任务依赖图 |
| Tasks | 任务卡片，点击查看输出 |
| Timeline | 执行时间线 |

---

## DAG 任务输出弹窗使用指南

### 1. 打开任务输出

- 在 **DAG** 页面点击任意任务节点
- 或在 **Tasks** 区域点击任务卡片
- 弹窗显示任务输出（Markdown + 代码高亮）
- 任务执行中输出会**实时刷新**，无需关闭弹窗

### 2. 弹窗顶部状态栏

弹窗顶部显示任务当前状态：

| 状态 | 颜色 | 含义 |
|------|------|------|
| RUNNING | 🟠 橙色 | 正在执行 |
| COMPLETED | 🟢 绿色 | 已完成 |
| FAILED | 🔴 红色 | 执行失败 |
| UNKNOWN | ⚫ 黑色 | 无数据 |

### 3. 分页查看

- 长输出自动分页（每页约 2000 字符）
- 使用 **◀ Prev** / **Next ▶** 切换
- 页码显示：`Page 2/5`
- 弹窗**记住每个任务的页码**，切换回来自动恢复

### 4. 搜索与高亮

- 在搜索框输入关键词
- 匹配内容**黄色高亮**
- 切换任务/分页后搜索词自动保存
- ⚠️ 搜索时暂停自动滚动，方便查看匹配位置

### 5. 自动滚动

- 默认自动滚到底部（终端风格）
- 实时执行时可看到最新输出
- 搜索模式下暂停自动滚动

### 6. 下载任务输出

- 点击 **📥 Save** 按钮
- 自动合并所有分页，生成 `.md` 文件下载
- 文件名：`{taskId}_output.md`
- 支持离线查看、团队共享、归档

### 7. 弹窗关闭与状态保存

- 点击 **×** 关闭弹窗
- 自动保存：当前页码、搜索词、滚动位置
- 下次打开同一任务恢复到上次位置

---

## API 使用

### 提交任务

```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze GitHub repository https://github.com/user/repo"}'
```

### 登录获取 Token

```bash
curl -X POST http://localhost:8000/auth/token \
  -d "username=admin&password=admin123"
```

### 查看 DLQ

```bash
curl http://localhost:8000/dlq
```

### 查看 Workflow 状态

```bash
curl http://localhost:8000/workflow/{workflow_id}
```

### 重试 DLQ 任务

```bash
curl -X POST http://localhost:8000/dlq/retry
```

---

## 配置参数

所有配置在 `.env` 中设置：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `OPENAI_API_KEY` | - | OpenAI API 密钥（必填） |
| `MODEL_PROVIDER` | `openai` | LLM 提供商 |
| `OPENAI_TIMEOUT` | `60` | OpenAI 超时（秒） |
| `MAX_RETRY` | `3` | 最大重试次数 |
| `BULKHEAD_RESEARCH` | `5` | Research 并发数 |
| `BULKHEAD_CODING` | `3` | Coding 并发数 |
| `CIRCUIT_BREAKER_THRESHOLD` | `3` | 熔断阈值 |
| `AGENT_TIMEOUT` | `120` | Agent 超时（秒） |
| `DLQ_RETRY_INTERVAL` | `10` | DLQ 重试间隔（秒） |

---

## 故障排查

### 任务卡住不动

1. 检查 `/health/breakers` 是否有熔断
2. 检查 `/dlq` 是否有失败任务
3. 检查 `.env` 中 API Key 是否正确

### WebSocket 无数据

1. 确认后端已启动（`uvicorn backend.main:app`）
2. 检查浏览器控制台是否有连接错误
3. 刷新页面重新连接

### DLQ 任务堆积

1. `GET /dlq` 查看失败原因
2. `POST /dlq/retry` 手动重试
3. `DELETE /dlq/clear` 清空

---

## 注意事项

- 弹窗依赖 `marked.js` 和 `prism.js`（CDN 引入）
- 实时刷新间隔 1 秒
- 输出分页 2000 字符/页
- 自动滚动仅在未搜索时生效
