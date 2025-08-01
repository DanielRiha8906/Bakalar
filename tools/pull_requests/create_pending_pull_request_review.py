from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("create_pending_pull_request_review")
def create_pending_pull_request_review_tool(owner: str, repo: str, pullNumber: int, commitID: Optional[str] = None) -> str:
    """
    Create a pending review for a pull request using MCP.
    
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to create a pending review for.
        commitID (str, optional): The commit ID to associate with the pending review. If not provided, the latest commit will be used.
    Example: 'owner = DanieLRiha8906', 'repo = Test-MCP', 'pullNumber = 3', 'commitID = abc123def456'
    """

    try:

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }
        if commitID is not None:
            payload["commitID"] = commitID

        result = call_mcp("create_pending_pull_request_review", payload)
        if "error" in result:
            return f"Failed to create pending review: {result['error']}"
        

        return f"Pending review created for PR #{pullNumber} on commit {commitID}."

    except Exception as e:
        return f"Exception during create_pending_pull_request_review: {str(e)}"
