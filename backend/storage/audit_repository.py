from sqlalchemy import select

from backend.storage.database import AsyncSessionLocal
from backend.storage.models import AuditLog


class AuditRepository:

    async def add_log(
        self,
        user: str,
        role: str,
        action: str,
        target: str = None,
    ):
        async with AsyncSessionLocal() as db:
            log = AuditLog(
                user=user,
                role=role,
                action=action,
                target=target,
            )
            db.add(log)
            await db.commit()
            return log

    async def get_logs(self, limit: int = 100):
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(AuditLog)
                .order_by(AuditLog.id.desc())
                .limit(limit)
            )
            return result.scalars().all()


audit_repo = AuditRepository()
