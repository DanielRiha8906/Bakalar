from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("merge_pull_request")
def merge_pull_request_tool(input: str) -> str:
    """
    Merge a pull request in a GitHub repository using MCP.
    Input format: 'owner/repo|pull_number|[merge_method]|[commit_title]|[commit_message]'
    Example: 'DanielRiha8906/Test-MCP|3|squash|Merge feature X|Squashed feature branch into main'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.split("|")
        if len(parts) < 2:
            return "Error: Invalid input. Format: 'owner/repo|pull_number|[merge_method]|[commit_title]|[commit_message]'"

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number
        }

        if len(parts) > 2 and parts[2]:
            payload["merge_method"] = parts[2]  # merge, squash, or rebase
        if len(parts) > 3 and parts[3]:
            payload["commit_title"] = parts[3]
        if len(parts) > 4 and parts[4]:
            payload["commit_message"] = parts[4]

        result = call_mcp("merge_pull_request", payload)
        if "error" in result:
            return f"Merge failed: {result['error']}"

        return f"Pull request #{pull_number} in '{owner}/{repo}' merged successfully."

    except Exception as e:
        return f"Exception during merge_pull_request: {str(e)}"
