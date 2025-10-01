from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json
from typing import Optional

@tool("search_repositories")
def search_repositories_tool(query: str, page: Optional[int] = 1, perPage: Optional[int] = 10 ) -> str:
    """
    Search for GitHub repositories owned by a specific user using MCP.
    Args:
        query: The search query string, typically the username.
        page: Page number for pagination (default is 1).
        perPage: Number of results per page (default is 10).

    Example: 
        'DanielRiha8906'
    Returns:
        A string listing all repositories owned by the user in the format:
    """
    try:

        if not query.strip():
            return "Error: query must not be empty."


        payload = {"query": query,
                   "page": page,
                   "perPage": perPage}
        
        result = call_mcp("search_repositories", payload)
       
        if isinstance(result, str):
            return f"Unexpected response: {result}"

        if "error" in result:
            return f"Search failed: {result['error'].get('message', str(result['error']))}"


        raw_content = result.get("result", {}).get("content", [])
        if not raw_content:
            return "No repositories found."

        repo_names = []
        for entry in raw_content:
            if isinstance(entry, dict) and "text" in entry:
                try:
                    parsed = json.loads(entry["text"])
                    for repo in parsed.get("items", []):
                        name = repo.get("full_name", "unknown")
                        desc = repo.get("description")
                        line = f"{name} - {desc}" if desc else name
                        repo_names.append(line)

                except Exception as parse_error:
                    return f"Error parsing JSON content: {parse_error}"

        return "\n".join(repo_names) if repo_names else "No repositories found."

    except Exception as e:
        return f"Exception during search_repositories: {str(e)}"
