from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_pull_request_diff")
def get_pull_request_diff_tool(owner: str, repo: str, pullNumber: int) -> str:
    """
    Get the diff of a specific pull request from a GitHub repository using MCP.
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to get the diff for.
    Returns:
        str: The diff of the pull request or an error message if the operation fails.
    Example: 'owner = DanielRiha8906', 'repo = Test-MCP', 'pullNumber = 3'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }

        result = call_mcp("get_pull_request_diff", payload)
        if "error" in result:
            return f"Get pull request diff failed: {result['error']}"

        return result.get("result", "No diff returned.")

    except Exception as e:
        return f"Exception during get_pull_request_diff: {str(e)}"
