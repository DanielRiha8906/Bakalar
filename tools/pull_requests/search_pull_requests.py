from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("search_pull_requests")
def search_pull_requests_tool(input: str) -> str:
    """
    Search for pull requests in GitHub repositories using query syntax.
    Input format: 'query|[owner]|[repo]|[sort]|[order]|[page]|[perPage]'
    Example: 'is:open is:pr author:DanielRiha8906|DanielRiha8906|Test-MCP|created|desc|1|5'
    """
    try:
        parts = input.split("|")
        if len(parts) < 1:
            return "Error: Invalid input. Format: 'query|[owner]|[repo]|[sort]|[order]|[page]|[perPage]'"

        query = parts[0]
        payload = {
            "query": query
        }

        if len(parts) > 1 and parts[1]: payload["owner"] = parts[1]
        if len(parts) > 2 and parts[2]: payload["repo"] = parts[2]
        if len(parts) > 3 and parts[3]: payload["sort"] = parts[3]
        if len(parts) > 4 and parts[4]: payload["order"] = parts[4]
        if len(parts) > 5 and parts[5]: payload["page"] = str(int(parts[5]))
        if len(parts) > 6 and parts[6]: payload["perPage"] = str(int(parts[6]))

        result = call_mcp("search_pull_requests", payload)
        if "error" in result:
            return f"Search failed: {result['error']}"

        return result.get("result", "No results returned.")

    except Exception as e:
        return f"Exception during search_pull_requests: {str(e)}"
