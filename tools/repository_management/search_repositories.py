from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("search_repositories")
def search_repositories_tool(input: str) -> str:
    """
    Search for GitHub repositories owned by a specific user using MCP.
    Input: GitHub username (e.g., 'DanielRiha8906')
    """
    try:
        query = f"user:{input}"
        payload = {"query": query}

        result = call_mcp("search_repositories", payload)
        
        if isinstance(result, str):
            return f"Unexpected response: {result}"

        if "error" in result:
            return f"Search failed: {result['error']}"

        raw_content = result.get("result", {}).get("content", [])
        if not raw_content:
            return "No repositories found."

        repo_names = []
        for entry in raw_content:
            if isinstance(entry, dict) and "text" in entry:
                try:
                    parsed = json.loads(entry["text"])
                    for repo in parsed.get("items", []):
                        repo_names.append(repo.get("full_name", "unknown"))
                except Exception as parse_error:
                    return f"Error parsing JSON content: {parse_error}"

        return "\n".join(repo_names) if repo_names else "No repositories found."

    except Exception as e:
        return f"Exception during search_repositories: {str(e)}"
