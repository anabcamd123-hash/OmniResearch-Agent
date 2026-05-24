"""
Audit API — 审计日志查询（仅 admin）
"""

from fastapi import APIRouter, Depends

from backend.utils.permissions import (
    require_role,
)
from backend.storage.audit_repository import audit_repo

router = APIRouter(
    prefix="/audit", tags=["audit"]
)


@router.get("/logs")
async def get_audit_logs(
    current_user=Depends(require_role("admin")),
    limit: int = 100,
):
    """查询审计日志（仅 admin）"""
    logs = await audit_repo.get_logs(limit=limit)
    return {"count": len(logs), "logs": logs}
