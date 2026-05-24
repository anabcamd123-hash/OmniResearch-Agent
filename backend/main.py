from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.api.routes_task import router as task_router
from backend.api.routes_ws import router as ws_router
from backend.api.routes_dashboard import router as dashboard_router
from backend.api.routes_history import router as history_router
from backend.api.routes_db import router as db_router
from backend.api.routes_upload import router as upload_router
from backend.api.routes_memory import router as memory_router
from backend.api.routes_trace import router as trace_router
from backend.api.routes_metrics import router as metrics_router
from backend.api.routes_health import router as health_router
from backend.api.routes_workflow import router as workflow_router
from backend.api.routes_dlq import router as dlq_router
from backend.api.routes_executor import router as executor_router
from backend.api.routes_dashboard_ws import router as dashboard_ws_router
from backend.api.routes_dashboard_actions import router as dashboard_actions_router
from backend.api.routes_task_logs import router as task_logs_router
from backend.api.routes_dashboard_search import router as dashboard_search_router
from backend.api.routes_auth import router as auth_router
from backend.api.routes_logs_export import router as export_router
from backend.api.routes_task_retry import router as task_retry_router
from backend.api.routes_audit import router as audit_router
from backend.storage.init_db import init_db
from backend.rag.rag_service import rag_service
from backend.runtime.register_events import register_events
from backend.utils.logger import logger

app = FastAPI(
    title="OmniResearch Agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(task_router)
app.include_router(ws_router)
app.include_router(dashboard_router)
app.include_router(history_router)
app.include_router(db_router)
app.include_router(upload_router)
app.include_router(memory_router)
app.include_router(trace_router)
app.include_router(metrics_router)
app.include_router(workflow_router)
app.include_router(dlq_router)
app.include_router(executor_router)
app.include_router(dashboard_ws_router)
app.include_router(dashboard_actions_router)
app.include_router(task_logs_router)
app.include_router(dashboard_search_router)
app.include_router(auth_router)
app.include_router(export_router)
app.include_router(task_retry_router)
app.include_router(audit_router)


# ── Frontend 静态文件 ──
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


@app.on_event("startup")
async def startup():
    await init_db()
    # RAG 索引异步构建，不阻塞启动
    import asyncio
    asyncio.create_task(rag_service.build_index())
    register_events()


@app.on_event("shutdown")
async def shutdown():
    pass


@app.get("/")
async def root():
    return {
        "message": "OmniResearch Agent Running",
        "version": "1.0.0",
        "docs": "/docs",
    }
