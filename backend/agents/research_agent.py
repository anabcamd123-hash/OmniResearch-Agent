from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.tools.web_search import WebSearch
from backend.tools.github_analyzer import GithubAnalyzer
from backend.tools.tool_router import ToolRouter
from backend.rag.vector_store import vector_store
from backend.rag.retriever import Retriever
from backend.memory.memory_store import memory
from backend.llm.provider_factory import get_provider

web_search = WebSearch()
github = GithubAnalyzer()
router = ToolRouter()
retriever = Retriever(vector_store)
llm = get_provider()


class ResearchAgent:

    def run(self, task: str):

        state.agent_status["research"] = "running"

        state.timeline.append({
            "agent": "Research",
            "event": "started"
        })

        logger.info(
            "[ResearchAgent] Analyzing task..."
        )

        # Tool Router selects tool
        tool = router.select(task)

        logger.info(
            f"[ResearchAgent] Tool selected: {tool}"
        )

        sources_text = ""
        github_text = ""
        rag_context = ""
        search_results = []
        github_data = None

        # === GitHub ===
        if tool == "github":
            parts = task.split("/")
            if len(parts) >= 2:
                owner = parts[-2].split()[-1]
                repo = parts[-1].split()[0]
                github_data = (
                    github.analyze_repo(
                        owner, repo
                    )
                )
                github_text = f"""
GitHub: {github_data.get('url')}
Stars: {github_data.get('stars')}
Forks: {github_data.get('forks')}
Description: {github_data.get('description')}
"""
                logger.info(
                    f"[ResearchAgent] GitHub: "
                    f"{owner}/{repo} "
                    f"stars="
                    f"{github_data.get('stars')}"
                )

        # === PDF / RAG ===
        if tool == "pdf":
            try:
                rag_results = retriever.retrieve(
                    task, k=3
                )
                if rag_results:
                    rag_context = (
                        "Document Context:\n"
                        + "\n---\n".join(
                            rag_results
                        )
                    )
                    logger.info(
                        f"[ResearchAgent] "
                        f"RAG: {len(rag_results)} chunks"
                    )
            except Exception as e:
                logger.info(
                    f"[ResearchAgent] RAG error: {e}"
                )

        # === Web Search ===
        if tool == "web" or (
            not github_text and not rag_context
        ):
            search_results = (
                web_search.search(task)
            )
            sources_text = "\n".join([
                f"- {s['title']}: {s['snippet']}"
                for s in search_results[:3]
            ])
            logger.info(
                f"[ResearchAgent] Web: "
                f"{len(search_results)} sources"
            )

        # LLM Summary
        summary = llm.invoke(
            f"""
Summarize the following research results.

Task: {task}

{f"Sources:\n{sources_text}" if sources_text else ""}
{github_text if github_text else ""}
{rag_context if rag_context else ""}

Provide a concise summary (2-3 sentences).
"""
        )

        result = {
            "summary": summary,
            "tool_used": tool,
            "sources": [
                s["url"]
                for s in search_results[:3]
            ],
            "search_results": search_results,
            "github": github_data,
            "rag_context": rag_context
        }

        # Save to memory
        memory.add(result)

        log_tokens(120)

        logger.info(
            "[ResearchAgent] Research completed"
        )

        state.agent_status["research"] = (
            "completed"
        )

        state.timeline.append({
            "agent": "Research",
            "event": "completed"
        })

        return result
