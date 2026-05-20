from fastapi import FastAPI

from backend.api.routes_task import router as task_router

app = FastAPI()

app.include_router(task_router)

@app.get("/")
async def root():
    return {
        "message": "OmniResearch Agent Running"
    }
