from sqlalchemy import select, delete

from .database import AsyncSessionLocal
from .models import (
    TaskRecord,
    WorkflowRecord,
    TokenUsage,
    LogRecord,
    MemoryRecord,
)


class TaskRepository:

    async def create_task(
        self,
        task_id: str,
        objective: str,
    ):

        async with AsyncSessionLocal() as db:

            task = TaskRecord(
                task_id=task_id,
                objective=objective,
                status="pending",
            )

            db.add(task)

            await db.commit()

            return task

    async def update_status(
        self,
        task_id: str,
        status: str,
    ):

        async with AsyncSessionLocal() as db:

            stmt = select(TaskRecord).where(
                TaskRecord.task_id == task_id
            )

            result = await db.execute(stmt)

            task = result.scalar_one_or_none()

            if task:
                task.status = status

                await db.commit()

    async def save_result(
        self,
        task_id: str,
        result_text: str,
        duration: float = None,
    ):

        async with AsyncSessionLocal() as db:

            stmt = select(TaskRecord).where(
                TaskRecord.task_id == task_id
            )

            result = await db.execute(stmt)

            task = result.scalar_one_or_none()

            if task:
                task.result = result_text
                task.duration = duration

                await db.commit()

    async def get_task(self, task_id):

        async with AsyncSessionLocal() as db:

            stmt = select(TaskRecord).where(
                TaskRecord.task_id == task_id
            )

            result = await db.execute(stmt)

            return result.scalar_one_or_none()

    async def update_retry(
        self,
        task_id: str,
        count: int,
    ):

        async with AsyncSessionLocal() as db:

            stmt = select(TaskRecord).where(
                TaskRecord.task_id == task_id
            )

            result = await db.execute(stmt)

            task = result.scalar_one_or_none()

            if task:
                task.retry_count = count

                await db.commit()

    async def list_tasks(
        self, limit=50
    ):

        async with AsyncSessionLocal() as db:

            stmt = (
                select(TaskRecord)
                .order_by(
                    TaskRecord.created_at.desc()
                )
                .limit(limit)
            )

            result = await db.execute(stmt)

            return result.scalars().all()


class WorkflowRepository:

    async def create_workflow(
        self,
        workflow_id: str,
        objective: str,
        total_tasks: int,
    ):

        async with AsyncSessionLocal() as db:

            workflow = WorkflowRecord(
                workflow_id=workflow_id,
                objective=objective,
                status="pending",
                total_tasks=total_tasks,
                completed_tasks=0,
            )

            db.add(workflow)

            await db.commit()

            return workflow

    async def update_status(
        self,
        workflow_id: str,
        status: str,
    ):

        async with AsyncSessionLocal() as db:

            stmt = select(WorkflowRecord).where(
                WorkflowRecord.workflow_id
                == workflow_id
            )

            result = await db.execute(stmt)

            wf = result.scalar_one_or_none()

            if wf:
                wf.status = status

                await db.commit()

    async def complete_workflow(
        self,
        workflow_id: str,
        completed_tasks: int,
        token_usage: int,
    ):

        async with AsyncSessionLocal() as db:

            stmt = select(WorkflowRecord).where(
                WorkflowRecord.workflow_id
                == workflow_id
            )

            result = await db.execute(stmt)

            wf = result.scalar_one_or_none()

            if wf:
                wf.status = "completed"
                wf.completed_tasks = (
                    completed_tasks
                )
                wf.token_usage = token_usage

                await db.commit()

    async def list_workflows(
        self, limit=20
    ):

        async with AsyncSessionLocal() as db:

            stmt = (
                select(WorkflowRecord)
                .order_by(
                    WorkflowRecord
                    .created_at.desc()
                )
                .limit(limit)
            )

            result = await db.execute(stmt)

            return result.scalars().all()


class TokenRepository:

    async def record_usage(
        self,
        task_id: str,
        agent: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
    ):

        async with AsyncSessionLocal() as db:

            record = TokenUsage(
                task_id=task_id,
                agent=agent,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

            db.add(record)

            await db.commit()

    async def get_total(self):

        async with AsyncSessionLocal() as db:

            from sqlalchemy import func

            stmt = select(
                func.sum(TokenUsage.total_tokens)
            )

            result = await db.execute(stmt)

            total = result.scalar()

            return total or 0


class LogRepository:

    async def add_log(
        self,
        message: str,
        level: str = "INFO",
    ):

        async with AsyncSessionLocal() as db:

            record = LogRecord(
                message=message,
                level=level,
            )

            db.add(record)

            await db.commit()

    async def list_logs(
        self, limit=100
    ):

        async with AsyncSessionLocal() as db:

            stmt = (
                select(LogRecord)
                .order_by(
                    LogRecord.created_at.desc()
                )
                .limit(limit)
            )

            result = await db.execute(stmt)

            return result.scalars().all()


class MemoryRepository:

    async def add_memory(
        self,
        content: str,
        source: str = "agent",
        memory_type: str = "general",
    ):

        async with AsyncSessionLocal() as db:

            record = MemoryRecord(
                content=content,
                source=source,
                memory_type=memory_type,
            )

            db.add(record)

            await db.commit()

    async def get_recent(
        self,
        limit: int = 20,
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(MemoryRecord)
                .order_by(
                    MemoryRecord.id.desc()
                )
                .limit(limit)
            )

            rows = result.scalars().all()

            return [
                {
                    "content": r.content,
                    "source": r.source,
                    "memory_type": r.memory_type,
                    "time": str(r.created_at),
                }
                for r in rows
            ]

    async def get_learning_memories(
        self,
        limit: int = 1000,
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(MemoryRecord)
                .where(
                    MemoryRecord.memory_type.in_(
                        ["success", "failure"]
                    )
                )
                .order_by(
                    MemoryRecord.id.desc()
                )
                .limit(limit)
            )

            rows = result.scalars().all()

            return [
                {
                    "content": r.content,
                    "memory_type": r.memory_type,
                    "time": str(r.created_at),
                }
                for r in rows
            ]

    async def clear(self):

        async with AsyncSessionLocal() as db:

            await db.execute(
                delete(MemoryRecord)
            )

            await db.commit()
