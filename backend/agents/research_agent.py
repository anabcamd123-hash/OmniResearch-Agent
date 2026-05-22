"""
ResearchAgent — 信息检索 + RAG + LLM 总结

自动调工具 + 查询历史 + 保存经验
"""

import asyncio

from backend.runtime.runtime_state import state
from backend.rag.rag_service import rag_service
from backend.tools.router import tool_router
from backend.memory.memory_store import memory
from backend.llm.provider_factory import get_provider
from backend.utils.logger import logger

llm = get_provider()


class ResearchAgent:

    async def run(self, task_desc: str):
        state.agent_status["research"] = "running"
        state.timeline.append(
            {
                "agent": "Research",
                "event": "started",
            }
        )
        logger.info(
            f"[Research] Analyzing: "
            f"{task_desc[:50]}"
        )

        # 工具调用
        tool_result = await tool_router.execute(
            task_desc
        )

        # 查询历史知识
        rag_results = []
        try:
            rag_results = await rag_service.query(
                task_desc, top_k=3
            )
        except Exception:
            pass

        context_text = (
            "\n---\n".join(rag_results)
            if rag_results
            else ""
        )

        # LLM 生成总结
        prompt = f"""
Summarize the research results.

Task: {task_desc}
Tool Result: {tool_result}
{f"Historical Context: {context_text}" if context_text else ""}

Return 2-3 sentences summary.
"""

        summary = await asyncio.to_thread(
            llm.invoke, prompt
        )

        # 保存经验
        try:
            await memory.add(
                {
                    "summary": summary,
                    "task": task_desc,
                },
                source="research",
            )
            await rag_service.add(summary)
        except Exception:
            pass

        state.agent_status["research"] = (
            "completed"
        )
        state.timeline.append(
            {
                "agent": "Research",
                "event": "completed",
            }
        )

        logger.info("[Research] Completed")

        return {
            "summary": summary,
            "tool_result": str(tool_result),
            "rag_context": context_text,
        }
