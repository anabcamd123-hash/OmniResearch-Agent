from backend.runtime.trace_store import trace_store


async def collect_trace(payload):

    event_type = payload.get(
        "_event_type", "unknown"
    )

    trace_store.add(event_type, payload)
