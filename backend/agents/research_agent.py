from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.tools.web_search import WebSearch
from backend.tools.github_analyzer import GithubAnalyzer
from backend.memory.memory_store import memory

web_search = WebSearch()
github = GithubAnalyzer()


class ResearchAgent:

    def run(self, task: str):

        state.agent_status["research"] = "running"

        state.timeline.append({
            "agent": "Research",
            "event": "started"
        })

        logger.info("[ResearchAgent] Searching knowledge base...")

        # Web Search
        search_results = web_search.search(task)
        logger.info(
            f"[ResearchAgent] Found "
            f"{len(search_results)} sources"
        )

        # GitHub Analysis
        github_data = None
        if "github" in task.lower() or "/" in task:
            parts = task.split("/")
            if len(parts) >= 2:
                owner = parts[-2].split()[-1]
                repo = parts[-1].split()[0]
                github_data = github.analyze_repo(
                    owner, repo
                )
                logger.info(
                    f"[ResearchAgent] GitHub: "
                    f"{owner}/{repo} "
                    f"stars={github_data.get('stars')}"
                )

        result = {
            "summary": f"Research completed for: {task}",
            "sources": [
                s["url"]
                for s in search_results[:3]
            ],
            "search_results": search_results,
            "github": github_data
        }

        # Save to memory
        memory.add(result)

        log_tokens(120)

        logger.info("[ResearchAgent] Research completed")

        state.agent_status["research"] = "completed"

        state.timeline.append({
            "agent": "Research",
            "event": "completed"
        })

        return result
