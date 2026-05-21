import requests
from backend.tools.base import BaseTool


class GitHubAnalyzerTool(BaseTool):

    name = "github"
    description = "Analyze GitHub repositories (stars, forks, issues)"

    async def run(self, input: str):

        parts = input.split("/")
        if len(parts) < 2:
            return {"error": "Invalid format. Use: owner/repo"}

        owner = parts[-2].split()[-1]
        repo = parts[-1].split()[0]

        url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}"
        )

        response = requests.get(url)
        data = response.json()

        return {
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "issues": data.get("open_issues_count"),
            "description": data.get("description", ""),
            "language": data.get("language", ""),
            "url": data.get("html_url", ""),
        }
