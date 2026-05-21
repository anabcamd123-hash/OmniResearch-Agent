import asyncio
from backend.agents.base_agent import BaseAgent
from backend.agents.result import AgentResult
from backend.executor.context import ExecutionContext
from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.runtime.events import bus
from backend.tools.router import tool_router
from backend.rag.rag_service import rag_service
from backend.memory.memory_store import memory
from backend.llm.provider_factory import get_provider

llm = get_provider()


class ResearchAgent(BaseAgent):

    async def run(
        self,
        task: str,
        context: ExecutionContext,
    ):

        state.agent_status["research"] = "running"
        state.timeline.append({
            "agent": "Research",
            "event": "started",
        })

        await bus.publish("agent_started", {
            "agent": "research",
            "task": task,
        })

        logger.info(
            "[ResearchAgent] Analyzing..."
        )

        # Tool execution
        tool_result = await tool_router.execute(task)

        # RAG context
        rag_context = ""
        try:
            rag_results = await rag_service.query(
                task, top_k=3
            )
            if rag_results:
                rag_context = (
                    "Historical context:\n"
                    + "\n---\n".join(rag_results)
                )
        except Exception:
            pass

        # LLM summarize
        summary = await asyncio.to_thread(
            llm.invoke,
            f"""
Summarize the following research results.

Task: {task}

Tool Result:
{tool_result}

{rag_context if rag_context else ""}

Provide a concise summary (2-3 sentences).
"""
        )

        result = AgentResult(
            success=True,
            content=summary,
            metadata={
                "tool_result": tool_result,
                "rag_context": rag_context,
            },
        )

        # Save to context for next agent
        context.set("research", result.content)

        await memory.add(
            result.to_dict(), source="research"
        )
        await rag_service.add(summary)
        log_tokens(120)

        logger.info(
            "[ResearchAgent] Completed"
        )

        state.agent_status["research"] = "completed"
        state.timeline.append({
            "agent": "Research",
            "event": "completed",
        })

        await bus.publish("agent_completed", {
            "agent": "research",
            "result": result.to_dict(),
        })

        return result
