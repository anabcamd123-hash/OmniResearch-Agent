from fastapi import APIRouter
from backend.runtime.metrics import metrics
from backend.runtime.agent_stats import agent_stats

router = APIRouter()


@router.get("/metrics")
async def get_metrics():

    return metrics.to_dict()


@router.get("/analytics/agents")
async def get_agent_analytics():

    return agent_stats.to_dict()


@router.get("/analytics/overview")
async def get_overview():

    m = metrics.to_dict()
    a = agent_stats.to_dict()

    total_calls = sum(
        v["calls"] for v in a.values()
    )

    avg_duration = 0
    if total_calls > 0:
        avg_duration = round(
            sum(
                v["total_duration"]
                for v in a.values()
            )
            / total_calls,
            2,
        )

    return {
        **m,
        "total_agent_calls": total_calls,
        "avg_agent_duration": avg_duration,
        "agents": a,
    }
