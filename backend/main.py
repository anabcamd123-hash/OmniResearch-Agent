from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from backend.storage.init_db import init_db
from backend.rag.rag_service import rag_service
from backend.runtime.register_events import register_events

app = FastAPI(title="OmniResearch Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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


@app.on_event("startup")
async def startup():
    await init_db()
    await rag_service.build_index()
    register_events()


@app.get("/")
async def root():
    return {
        "message": "OmniResearch Agent Running",
        "docs": "/docs",
    }
