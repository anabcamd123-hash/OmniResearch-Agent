from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes_task import router as task_router
from backend.api.routes_ws import router as ws_router
from backend.api.routes_dashboard import router as dashboard_router
from backend.api.routes_history import router as history_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(task_router)
app.include_router(ws_router)
app.include_router(dashboard_router)
app.include_router(history_router)

@app.get("/")
async def root():
    return {
        "message": "OmniResearch Agent Running"
    }
