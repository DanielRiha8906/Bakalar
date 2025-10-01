from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_pull_request_status")
def get_pull_request_status_tool(owner: str, repo: str, pullNumber: int) -> str:
    """
    Get the status checks of a pull request using MCP.
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to get the status for.
    Example: 'owner = DanielRiha8906', 'repo = Test-MCP', 'pullNumber = 3'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }

        result = call_mcp("get_pull_request_status", payload)
        if "error" in result:
            return f"Failed to get PR status: {result['error']}"

        return result.get("result", "No status found.")

    except Exception as e:
        return f"Exception during get_pull_request_status: {str(e)}"
