from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json
from typing import Optional

@tool("search_users")
def search_users_tool(query: str, page: Optional[int] = 1, perPage: Optional[int] = 10, order: Optional[str] = None, sort: Optional[str] = None) -> str:
    """
    Search for GitHub users using MCP.
    Args:
        query: The search query string, typically the username or part of it.
        page: Page number for pagination (default is 1).
        perPage: Number of results per page (default is 10).
        order: Optional order of results ("asc" or "desc").
        sort: Optional field to sort results by (e.g., "followers", "repositories", "joined").
    Example:
        'query=DanielRiha8906;sort=followers;order=desc;page=1;perPage=10'
    """
    try:

        payload = {
            "query": query,
            "page": page,
            "perPage": perPage,
            "order": order,
            "sort": sort
        }

        payload = {key: value for key, value in payload.items() if value is not None}
        
        result = call_mcp("search_users", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        data = json.loads(text)
        users = data.get("items", [])

        if not users:
            return "No users found."

        return "\n".join([
            f"{user['login']} — {user.get('html_url', '[no url]')}"
            for user in users[:5]
        ])

    except Exception as e:
        return f"Exception in search_users: {str(e)}"
