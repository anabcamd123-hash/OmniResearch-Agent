from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    TASK_STARTED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_RETRY,
    AGENT_STARTED,
    AGENT_COMPLETED,
    WORKFLOW_STARTED,
    WORKFLOW_COMPLETED,
)

from backend.runtime.listeners.logger_listener import (
    on_task_started as log_task_started,
    on_task_completed as log_task_completed,
    on_task_failed as log_task_failed,
    on_task_retry as log_task_retry,
    on_agent_started as log_agent_started,
    on_agent_completed as log_agent_completed,
    on_workflow_started as log_workflow_started,
    on_workflow_completed as log_workflow_completed,
)

from backend.runtime.listeners.dashboard_listener import (
    on_task_started as dash_task_started,
    on_task_completed as dash_task_completed,
    on_task_failed as dash_task_failed,
    on_task_retry as dash_task_retry,
    on_agent_started as dash_agent_started,
    on_agent_completed as dash_agent_completed,
    on_workflow_started as dash_workflow_started,
    on_workflow_completed as dash_workflow_completed,
)

from backend.runtime.listeners.websocket_listener import (
    on_task_started as ws_task_started,
    on_task_completed as ws_task_completed,
    on_task_failed as ws_task_failed,
    on_agent_started as ws_agent_started,
    on_agent_completed as ws_agent_completed,
    on_workflow_started as ws_workflow_started,
    on_workflow_completed as ws_workflow_completed,
)


def register_events():

    # Logger listener
    event_bus.subscribe(TASK_STARTED, log_task_started)
    event_bus.subscribe(TASK_COMPLETED, log_task_completed)
    event_bus.subscribe(TASK_FAILED, log_task_failed)
    event_bus.subscribe(TASK_RETRY, log_task_retry)
    event_bus.subscribe(AGENT_STARTED, log_agent_started)
    event_bus.subscribe(AGENT_COMPLETED, log_agent_completed)
    event_bus.subscribe(WORKFLOW_STARTED, log_workflow_started)
    event_bus.subscribe(WORKFLOW_COMPLETED, log_workflow_completed)

    # Dashboard listener
    event_bus.subscribe(TASK_STARTED, dash_task_started)
    event_bus.subscribe(TASK_COMPLETED, dash_task_completed)
    event_bus.subscribe(TASK_FAILED, dash_task_failed)
    event_bus.subscribe(TASK_RETRY, dash_task_retry)
    event_bus.subscribe(AGENT_STARTED, dash_agent_started)
    event_bus.subscribe(AGENT_COMPLETED, dash_agent_completed)
    event_bus.subscribe(WORKFLOW_STARTED, dash_workflow_started)
    event_bus.subscribe(WORKFLOW_COMPLETED, dash_workflow_completed)

    # WebSocket listener
    event_bus.subscribe(TASK_STARTED, ws_task_started)
    event_bus.subscribe(TASK_COMPLETED, ws_task_completed)
    event_bus.subscribe(TASK_FAILED, ws_task_failed)
    event_bus.subscribe(AGENT_STARTED, ws_agent_started)
    event_bus.subscribe(AGENT_COMPLETED, ws_agent_completed)
    event_bus.subscribe(WORKFLOW_STARTED, ws_workflow_started)
    event_bus.subscribe(WORKFLOW_COMPLETED, ws_workflow_completed)
