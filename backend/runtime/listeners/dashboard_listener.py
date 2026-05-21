from backend.runtime.runtime_state import state


async def on_task_started(payload):

    state.timeline.append({
        "event": "started",
        **payload,
    })


async def on_task_completed(payload):

    state.timeline.append({
        "event": "completed",
        **payload,
    })


async def on_task_failed(payload):

    state.timeline.append({
        "event": "failed",
        **payload,
    })


async def on_task_retry(payload):

    state.timeline.append({
        "event": "retry",
        **payload,
    })


async def on_agent_started(payload):

    agent = payload.get("agent", "")

    if agent in state.agent_status:
        state.agent_status[agent] = "running"


async def on_agent_completed(payload):

    agent = payload.get("agent", "")

    if agent in state.agent_status:
        state.agent_status[agent] = "completed"


async def on_workflow_started(payload):

    state.timeline.append({
        "event": "workflow_started",
        **payload,
    })


async def on_workflow_completed(payload):

    state.timeline.append({
        "event": "workflow_completed",
        **payload,
    })
