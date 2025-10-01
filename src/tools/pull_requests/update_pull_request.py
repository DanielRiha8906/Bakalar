from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("update_pull_request")
def update_pull_request_tool(owner: str, repo: str, pullNumber: int, title: Optional[str] = None, body: Optional[str] = None, state: Optional[str] = None, base: Optional[str] = None, maintainer_can_modify: Optional[bool] = None ) -> str:
    """
    Update an existing pull request in a GitHub repository using MCP.
    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to update.
        title (Optional[str]): The new title for the pull request.
        body (Optional[str]): The new body for the pull request.
        state (Optional[str]): The new state of the pull request (open or closed).
        base (Optional[str]): The new base branch for the pull request.
        maintainer_can_modify (Optional[bool]): Whether maintainers can modify the pull request.
    Returns:
        str: A message indicating the result of the update operation or an error message.
    Example:
        'owner = DanielRiha8906, repo = Test-MCP, pullNumber = 3, title = "Updated PR Title", body = "Updated PR Body", base = "main", state = "open", maintainer_can_modify = True'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if state is not None:
            payload["state"] = state
        if base is not None:
            payload["base"] = base
        if maintainer_can_modify is not None:
            payload["maintainer_can_modify"] = maintainer_can_modify
        
        result = call_mcp("update_pull_request", payload)
        if "error" in result:
            return f"Update pull request failed: {result['error']}"

        return f"Pull request #{pullNumber} in '{owner}/{repo}' updated successfully."

    except Exception as e:
        return f"Exception during update_pull_request: {str(e)}"
