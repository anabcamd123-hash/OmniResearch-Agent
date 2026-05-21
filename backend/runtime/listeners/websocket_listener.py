from backend.api.ws_manager import manager


async def on_task_started(payload):

    task_id = payload.get("task_id", "unknown")
    task_type = payload.get("task_type", "")

    await manager.broadcast(
        f"[Task] Started: {task_id} ({task_type})"
    )


async def on_task_completed(payload):

    task_id = payload.get("task_id", "unknown")
    duration = payload.get("duration", 0)

    await manager.broadcast(
        f"[Task] Completed: {task_id} "
        f"({duration:.2f}s)"
    )


async def on_task_failed(payload):

    task_id = payload.get("task_id", "unknown")

    await manager.broadcast(
        f"[Task] Failed: {task_id}"
    )


async def on_agent_started(payload):

    agent = payload.get("agent", "unknown")

    await manager.broadcast(
        f"[Agent] Started: {agent}"
    )


async def on_agent_completed(payload):

    agent = payload.get("agent", "unknown")

    await manager.broadcast(
        f"[Agent] Completed: {agent}"
    )


async def on_workflow_started(payload):

    workflow_id = payload.get(
        "workflow_id", "unknown"
    )

    await manager.broadcast(
        f"[Workflow] Started: {workflow_id}"
    )


async def on_workflow_completed(payload):

    workflow_id = payload.get(
        "workflow_id", "unknown"
    )

    await manager.broadcast(
        f"[Workflow] Completed: {workflow_id}"
    )
