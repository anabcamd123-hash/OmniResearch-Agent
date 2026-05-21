import requests


class GithubAnalyzer:

    def analyze_repo(
        self,
        owner,
        repo
    ):

        url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}"
        )

        response = requests.get(url)

        data = response.json()

        return {
            "stars":
                data.get("stargazers_count"),
            "forks":
                data.get("forks_count"),
            "issues":
                data.get("open_issues_count"),
            "description":
                data.get("description", ""),
            "language":
                data.get("language", ""),
            "url":
                data.get("html_url", "")
        }
