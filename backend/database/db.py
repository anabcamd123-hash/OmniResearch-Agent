import os
import json
import redis.asyncio as redis
from backend.database.repository import (
    init_db, get_session,
    TaskRecord, WorkflowRecord, LogRecord
)
from datetime import datetime

REDIS_URL = os.getenv(
    "REDIS_URL", "redis://redis:6379"
)

_pool = None


async def get_redis():
    global _pool
    if _pool is None:
        _pool = redis.from_url(
            REDIS_URL, decode_responses=True
        )
    return _pool


async def save_task_result(
    task_id: str, result: dict
):
    r = await get_redis()
    await r.set(
        f"task:{task_id}",
        json.dumps(result),
        ex=3600
    )


async def get_task_result(task_id: str):
    r = await get_redis()
    data = await r.get(f"task:{task_id}")
    return json.loads(data) if data else None


async def save_workflow(
    workflow_id: str, tasks: list
):
    r = await get_redis()
    await r.set(
        f"workflow:{workflow_id}",
        json.dumps(tasks),
        ex=86400
    )


async def get_workflow(workflow_id: str):
    r = await get_redis()
    data = await r.get(
        f"workflow:{workflow_id}"
    )
    return json.loads(data) if data else None


async def close_redis():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# SQLite persistence functions
def persist_task(
    task_id, task_type, status,
    retries=0, duration=None,
    output=None
):
    session = get_session()
    try:
        record = session.query(
            TaskRecord
        ).filter_by(task_id=task_id).first()

        if record:
            record.status = status
            record.retries = retries
            record.duration = duration
            record.output = output
        else:
            record = TaskRecord(
                task_id=task_id,
                task_type=task_type,
                status=status,
                retries=retries,
                duration=duration,
                output=output
            )
            session.add(record)

        session.commit()
    finally:
        session.close()


def persist_workflow(
    workflow_id, status,
    total_tasks, completed_tasks,
    token_usage=0
):
    session = get_session()
    try:
        record = session.query(
            WorkflowRecord
        ).filter_by(
            workflow_id=workflow_id
        ).first()

        if record:
            record.status = status
            record.total_tasks = total_tasks
            record.completed_tasks = completed_tasks
            record.token_usage = token_usage
        else:
            record = WorkflowRecord(
                workflow_id=workflow_id,
                status=status,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                token_usage=token_usage
            )
            session.add(record)

        session.commit()
    finally:
        session.close()


def persist_log(message, level="INFO"):
    session = get_session()
    try:
        record = LogRecord(
            message=message,
            level=level
        )
        session.add(record)
        session.commit()
    finally:
        session.close()


def get_all_tasks(limit=50):
    session = get_session()
    try:
        records = session.query(
            TaskRecord
        ).order_by(
            TaskRecord.created_at.desc()
        ).limit(limit).all()
        return [
            {
                "task_id": r.task_id,
                "task_type": r.task_type,
                "status": r.status,
                "retries": r.retries,
                "duration": r.duration,
                "created_at": str(r.created_at)
            }
            for r in records
        ]
    finally:
        session.close()


def get_all_workflows(limit=20):
    session = get_session()
    try:
        records = session.query(
            WorkflowRecord
        ).order_by(
            WorkflowRecord.created_at.desc()
        ).limit(limit).all()
        return [
            {
                "workflow_id": r.workflow_id,
                "status": r.status,
                "total_tasks": r.total_tasks,
                "completed_tasks": r.completed_tasks,
                "token_usage": r.token_usage,
                "created_at": str(r.created_at)
            }
            for r in records
        ]
    finally:
        session.close()
