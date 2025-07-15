from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json

@tool("get_commit_details")
def get_commit_tool(input: str) -> str:
    """
    Get details of a specific commit.
    Input format: 'owner/repo|commit_sha'
    Example: 'DanielRiha8906/NUM|0a67897f767ed0bc9d34b6988392d699f381f03f'
    """
    try:
        repo_info, sha = input.split("|")
        owner, repo = repo_info.split("/")
        payload = {"owner": owner, "repo": repo, "sha": sha}

        result = call_mcp("get_commit", payload)

        #error in call_mcp
        if "error" in result:
            return f"Error: {result['error']}"

        text = result["result"]["content"][0]["text"]
        data = json.loads(text)

        commit = data["commit"]
        msg = commit["message"].strip()
        author = commit["author"]["name"]
        date = commit["author"]["date"]

        return f"{msg}\nBy {author} on {date}"

    # General error
    except Exception as e:
        return f"Exception in get_commit: {str(e)}"