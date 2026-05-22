from fastapi import APIRouter
from backend.storage.database import AsyncSessionLocal
from backend.version import VERSION

router = APIRouter()


@router.get("/health")
async def health():

    return {
        "status": "ok",
        "version": VERSION,
    }


@router.get("/health/full")
async def full_health():

    checks = {"version": VERSION}

    # Database
    try:
        async with AsyncSessionLocal() as db:
            await db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Provider
    try:
        from backend.llm.provider_factory import get_provider
        get_provider()
        checks["provider"] = "ok"
    except Exception as e:
        checks["provider"] = f"error: {e}"

    # RAG
    try:
        from backend.rag.rag_service import rag_service
        await rag_service.query("test", top_k=1)
        checks["rag"] = "ok"
    except Exception as e:
        checks["rag"] = f"error: {e}"

    checks["status"] = "ok"

    return checks


@router.get("/health/breakers")
async def breaker_status():
    """熔断器状态（监控用）"""
    from backend.tools.router import tool_router
    return tool_router.get_breaker_status()


@router.get("/health/tools")
async def tool_audit_status():
    """工具审计统计（监控用）"""
    from backend.tools.tool_audit import tool_audit
    return tool_audit.get_stats()


@router.get("/health/tools/recent")
async def tool_recent_calls():
    """最近工具调用记录"""
    from backend.tools.tool_audit import tool_audit
    return tool_audit.get_recent()
