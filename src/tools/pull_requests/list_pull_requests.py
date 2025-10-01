from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("list_pull_requests")
def list_pull_requests_tool(
    owner: str,
    repo: str,
    state: Optional[str] = None,
    head: Optional[str] = None,
    base: Optional[str] = None,
    sort: Optional[str] = "created",
    direction: Optional[str] = "desc",
    page: Optional[int] = 1,
    perPage: Optional[int] = 20
) -> str:
    """
    List pull requests in a GitHub repository using MCP.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        state (Optional[str]): The state of the pull requests (open, closed, all).
        head (Optional[str]): The head branch of the pull request.
        base (Optional[str]): The base branch of the pull request.
        sort (Optional[str]): The field to sort by (created, updated, popularity, long-running).
        direction (Optional[str]): The direction to sort (asc or desc).
        page (Optional[int]): The page number for pagination.
        perPage (Optional[int]): Number of results per page.

    Returns:
        str: A string representation of the pull requests or an error message.
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo
        }

        if state: payload["state"] = state
        if head: payload["head"] = head
        if base: payload["base"] = base
        if sort: payload["sort"] = sort
        if direction: payload["direction"] = direction
        if page: payload["page"] = page
        if perPage: payload["perPage"] = perPage

        result = call_mcp("list_pull_requests", payload)

        if "error" in result:
            return f"Listing pull requests failed: {result['error']}"

        return result.get("result", "No pull requests found.")

    except Exception as e:
        return f"Exception during list_pull_requests: {str(e)}"
