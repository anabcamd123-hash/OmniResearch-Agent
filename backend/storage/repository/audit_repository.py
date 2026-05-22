"""
AuditRepository — 审计日志 CRUD
"""

from sqlalchemy import select

from backend.storage.database import (
    AsyncSessionLocal,
)
from backend.storage.models import AuditLog


class AuditRepository:

    async def add_log(
        self,
        user: str,
        role: str,
        action: str,
        target: str = None,
    ):
        """写入审计记录"""
        async with AsyncSessionLocal() as session:
            async with session.begin():
                log = AuditLog(
                    user=user,
                    role=role,
                    action=action,
                    target=target,
                )
                session.add(log)

    async def get_logs(
        self, limit: int = 100
    ) -> list[dict]:
        """查询审计日志"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AuditLog)
                .order_by(
                    AuditLog.created_at.desc()
                )
                .limit(limit)
            )
            rows = result.scalars().all()
            return [
                {
                    "user": l.user,
                    "role": l.role,
                    "action": l.action,
                    "target": l.target,
                    "timestamp": (
                        str(l.created_at)
                        if l.created_at
                        else ""
                    ),
                }
                for l in rows
            ]


audit_repo = AuditRepository()
