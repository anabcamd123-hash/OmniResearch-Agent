from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import ReflectionAgent

from backend.utils.logger import logger


class WorkflowExecutor:

    def __init__(self):

        self.planner = PlannerAgent()
        self.research = ResearchAgent()
        self.coding = CodingAgent()
        self.verify = VerifyAgent()
        self.reflection = ReflectionAgent()

    def execute(self, task: str):

        logger.info("[System] Starting workflow")

        plan = self.planner.create_plan(task)

        research_result = self.research.run(task)

        code_result = self.coding.run(research_result)

        verify_result = self.verify.run(code_result)

        reflection_result = self.reflection.run(verify_result)

        logger.info("[System] Workflow completed")

        return {
            "plan": plan,
            "research": research_result,
            "code": code_result,
            "verify": verify_result,
            "reflection": reflection_result
        }
