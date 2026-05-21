import asyncio
from backend.agents.base_agent import BaseAgent
from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.tools.router import tool_router
from backend.rag.rag_service import rag_service
from backend.memory.memory_store import memory
from backend.llm.provider_factory import get_provider

llm = get_provider()


class ResearchAgent(BaseAgent):

    async def run(self, task: str):

        state.agent_status["research"] = "running"

        state.timeline.append({
            "agent": "Research",
            "event": "started",
        })

        logger.info(
            "[ResearchAgent] Analyzing task..."
        )

        # Use tool router to execute
        tool_result = await tool_router.execute(task)

        # Get RAG context
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

        # LLM summarize (async)
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

        result = {
            "summary": summary,
            "tool_result": tool_result,
            "rag_context": rag_context,
        }

        # Save to memory (DB)
        await memory.add(result, source="research")

        # Add to RAG index
        await rag_service.add(summary)

        log_tokens(120)

        logger.info(
            "[ResearchAgent] Research completed"
        )

        state.agent_status["research"] = "completed"

        state.timeline.append({
            "agent": "Research",
            "event": "completed",
        })

        return result
