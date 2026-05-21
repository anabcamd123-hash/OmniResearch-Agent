from backend.utils.logger import logger


async def on_task_started(payload):

    task_id = payload.get("task_id", "unknown")
    task_type = payload.get("task_type", "")

    logger.info(
        f"[Task] Started: {task_id} ({task_type})"
    )


async def on_task_completed(payload):

    task_id = payload.get("task_id", "unknown")
    duration = payload.get("duration", 0)

    logger.info(
        f"[Task] Completed: {task_id} "
        f"({duration:.2f}s)"
    )


async def on_task_failed(payload):

    task_id = payload.get("task_id", "unknown")

    logger.info(
        f"[Task] Failed: {task_id}"
    )


async def on_task_retry(payload):

    task_id = payload.get("task_id", "unknown")
    retry = payload.get("retry", 0)
    reason = payload.get("reason", "")

    logger.info(
        f"[Task] Retry {retry}: {task_id} "
        f"- {reason[:50]}"
    )


async def on_agent_started(payload):

    agent = payload.get("agent", "unknown")

    logger.info(
        f"[Agent] Started: {agent}"
    )


async def on_agent_completed(payload):

    agent = payload.get("agent", "unknown")

    logger.info(
        f"[Agent] Completed: {agent}"
    )


async def on_workflow_started(payload):

    workflow_id = payload.get(
        "workflow_id", "unknown"
    )

    logger.info(
        f"[Workflow] Started: {workflow_id}"
    )


async def on_workflow_completed(payload):

    workflow_id = payload.get(
        "workflow_id", "unknown"
    )

    logger.info(
        f"[Workflow] Completed: {workflow_id}"
    )
