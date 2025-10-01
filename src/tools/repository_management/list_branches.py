from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json
import re
from typing import Optional

@tool("list_branches")
def list_branches_tool(owner: str, repo: str, perPage: Optional[int] = 10, page: Optional[int] = 1 ) -> str:
    """
    List all branches in a GitHub repository using MCP.
    
    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        perPage: Number of branches to return per page (default is 10).
        page: Page number for pagination (default is 1).
    
    Returns:
        A string listing all branches in the format:
    
    Example: 'DanielRiha8906/testicek'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "perPage": perPage,
            "page": page
        }

        payload = {key: value for key, value in payload.items() if value is not None}

        result = call_mcp("list_branches", payload)

        if "error" in result:
            return f"Branch listing failed: {result['error']}"

        content = result.get("result", {}).get("content", [])
        if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
            try:
                parsed = json.loads(content[0]["text"])
                branches = [entry.get("name", "unknown") for entry in parsed]
                return "Branches:\n" + "\n".join(f"- {b}" for b in branches) if branches else "No branches found."
            except Exception as e:
                return f"Error parsing branch list JSON: {e}"

        return f"Unexpected response format: {content}"

    except Exception as e:
        return f"Exception during list_branches: {str(e)}"
