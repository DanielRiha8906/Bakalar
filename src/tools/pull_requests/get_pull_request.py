from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_pull_request")
def get_pull_request_tool(owner: str, repo: str, pullNumber: int) -> str:
    """
    Get details of a specific pull request from a GitHub repository using MCP.
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to get details for.
    Returns:
        str: Details of the pull request or an error message if the operation fails.
    Example: 'owner = DanielRiha8906', 'repo = Test-MCP', 'pullNumber = 3'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }

        result = call_mcp("get_pull_request", payload)
        if "error" in result:
            return f"Get pull request failed: {result['error']}"

        return result.get("result", "No pull request found.")

    except Exception as e:
        return f"Exception during get_pull_request: {str(e)}"
