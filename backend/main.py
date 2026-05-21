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
from backend.database.repository import init_db

# Initialize SQLite database
init_db()

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
app.include_router(db_router)
app.include_router(upload_router)


@app.get("/")
async def root():
    return {
        "message": "OmniResearch Agent Running"
    }
