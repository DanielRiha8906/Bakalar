from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("search_pull_requests")
def search_pull_requests_tool(query: str, owner: Optional[str] = None, repo: Optional[str] = None, sort: Optional[str] = None, order: Optional[str] = "desc", page: Optional[int] = 1, perPage: Optional[int] = 20  ) -> str:
    """
    Search for pull requests in GitHub repositories using query syntax.
    Args: 
        query (str): The search query string.
        owner (Optional[str]): The owner of the repository to filter by.
        repo (Optional[str]): The repository to filter by.
        sort (Optional[str]): The field to sort by (created, updated, popularity, long-running).
        order (Optional[str]): The order of the results (asc or desc).
        page (Optional[int]): The page number for pagination.
        perPage (Optional[int]): Number of results per page.
    Returns:
        str: A string representation of the search results or an error message.
    Example: 'is:pr is:open author:DanielRiha8906 repo:DanielRiha8906/Test-MCP sort:created order:desc page:1 perPage:20'
    """
    try:
        payload = {
            "query": query
        }
        if owner:
            payload["owner"] = owner
        if repo:
            payload["repo"] = repo
        if sort:
            payload["sort"] = sort
        if order:
            payload["order"] = order
        if page:
            payload["page"] = page
        if perPage:
            payload["perPage"] = perPage
            
        result = call_mcp("search_pull_requests", payload)
        if "error" in result:
            return f"Search failed: {result['error']}"

        return result.get("result", "No results returned.")

    except Exception as e:
        return f"Exception during search_pull_requests: {str(e)}"
