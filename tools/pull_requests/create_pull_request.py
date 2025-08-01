from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("create_pull_request")
def create_pull_request_tool(owner: str, repo: str, title: str, head: str, base: str, body: Optional[str] = None, draft: Optional[bool] = False, maintainer_can_modify: Optional[bool] = False ) -> str:
    """
    Create a new pull request in a GitHub repository using MCP.
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        title (str): The title of the pull request.
        head (str): The name of the branch where your changes are implemented.
        base (str): The name of the branch you want the changes pulled into.
        body (str, optional): The content of the pull request description.
        draft (bool, optional): If True, creates a draft pull request. Defaults to False.
        maintainer_can_modify (bool, optional): If True, allows maintainers to modify the pull request. Defaults to False.
    Example: 'owner = DanielRiha8906', 'repo = Test-MCP', 'title = "New Feature"', 'head = "feature-branch"', 'base = "main"'
    Raises:
        ValueError: If required parameters are missing or invalid.
        Exception: If there is an error during the MCP call.
    Returns:
        str: A message indicating the result of the pull request creation.
    
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "title": title,
            "head": head,
            "base": base,
        }
        if body is not None:
            payload["body"] = body
        if draft is not None and isinstance(draft, bool):
            payload["draft"] = draft

        if maintainer_can_modify is not None and isinstance(maintainer_can_modify, bool):
            payload["maintainer_can_modify"] = maintainer_can_modify

        result = call_mcp("create_pull_request", payload)
        if "error" in result:
            return f"Pull request creation failed: {result['error']}"
        return f"Pull request '{title}' created from '{head}' into '{base}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during create_pull_request: {str(e)}"
