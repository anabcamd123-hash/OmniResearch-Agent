from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import ReflectionAgent

from backend.utils.logger import stream_log


class WorkflowExecutor:

    def __init__(self):

        self.planner = PlannerAgent()
        self.research = ResearchAgent()
        self.coding = CodingAgent()
        self.verify = VerifyAgent()
        self.reflection = ReflectionAgent()

    async def execute(self, task: str):

        await stream_log("[System] Starting workflow")

        plan = await self.planner.create_plan(task)

        research_result = self.research.run(task)

        await stream_log("[ResearchAgent] Searching knowledge base...")

        code_result = self.coding.run(research_result)

        await stream_log("[CodingAgent] Generating code")

        verify_result = self.verify.run(code_result)

        await stream_log("[VerifyAgent] Verification passed")

        reflection_result = self.reflection.run(verify_result)

        await stream_log("[ReflectionAgent] Evaluating result quality...")

        await stream_log("[System] Workflow completed")

        return {
            "plan": plan,
            "research": research_result,
            "code": code_result,
            "verify": verify_result,
            "reflection": reflection_result
        }
