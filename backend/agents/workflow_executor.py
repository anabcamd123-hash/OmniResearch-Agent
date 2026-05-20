class WorkflowExecutor:

    async def execute(self, task: str):

        await stream_log("[System] Starting workflow")

        plan = await self.planner.create_plan(task)

        research_result = self.research.run(task)

        code_result = self.coding.run(research_result)

        verify_result = self.verify.run(code_result)

        reflection_result = self.reflection.run(verify_result)

        await stream_log("[System] Workflow completed")

        return {
            "plan": plan,
            "research": research_result,
            "code": code_result,
            "verify": verify_result,
            "reflection": reflection_result
        }
