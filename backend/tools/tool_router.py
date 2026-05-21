class ToolRouter:

    def select(self, task):

        task_lower = task.lower()

        if (
            "github" in task_lower
            or ".com/" in task_lower
        ):
            return "github"

        if (
            "paper" in task_lower
            or "pdf" in task_lower
            or "arxiv" in task_lower
            or "upload" in task_lower
        ):
            return "pdf"

        return "web"
