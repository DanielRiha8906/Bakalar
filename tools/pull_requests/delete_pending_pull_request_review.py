from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("delete_pending_pull_request_review")
def delete_pending_pull_request_review_tool(owner: str, repo: str, pullNumber: int) -> str:
    """
    Delete the latest pending pull request review using MCP.
    
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to delete the pending review for.
    Example: 'owner = DanielRiha8906', 'repo = Test-MCP', 'pullNumber = 3'

    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }

        result = call_mcp("delete_pending_pull_request_review", payload)
        if "error" in result:
            return f"Failed to delete pending review: {result['error']}"

        return f"Pending review for PR #{pullNumber} in '{owner}/{repo}' was deleted."

    except Exception as e:
        return f"Exception during delete_pending_pull_request_review: {str(e)}"
