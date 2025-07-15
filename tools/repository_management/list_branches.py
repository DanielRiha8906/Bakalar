from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json

@tool("list_branches")
def list_branches_tool(input: str) -> str:
    """
    List all branches in a GitHub repository using MCP.
    Input format: 'owner/repo'
    Example: 'DanielRiha8906/Test-MCP'
    """
    try:
        owner, repo = input.strip().strip("'\"").split("/")
        repo = repo.strip().strip("'").strip('"').replace("\n", "").replace("\n", "")
        payload = {
            "owner": owner,
            "repo": repo
        }

        result = call_mcp("list_branches", payload)

        if "error" in result:
            return f"Branch listing failed: {result['error']}"

        content = result.get("result", {}).get("content", [])
        if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
            try:
                parsed = json.loads(content[0]["text"])
                branches = [entry.get("name", "unknown") for entry in parsed]
                return "\n".join(branches) if branches else "No branches found."
            except Exception as e:
                return f"Error parsing branch list JSON: {e}"

        return f"Unexpected response format: {content}"

    except Exception as e:
        return f"Exception during list_branches: {str(e)}"
 