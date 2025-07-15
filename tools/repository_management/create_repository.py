from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool

@tool("create_repository")
def create_repository_tool(input: str) -> str:
    """
    Create a new GitHub repository using MCP.
    Input format: 'repo_name|description|private|autoInit'
    Example: 'my-new-repo|My test repo|true|true'
    """
    try:
        parts = input.split("|")
        name = parts[0]
        description = parts[1] if len(parts) > 1 else ""
        private = parts[2].lower() == "true" if len(parts) > 2 else True
        autoInit = parts[3].lower() == "true" if len(parts) > 3 else True

        payload = {
            "name": name,
            "description": description,
            "private": private,
            "autoInit": autoInit
        }

        result = call_mcp("create_repository", payload)
        if "error" in result:
            return f"Failed to create repo: {result['error']}"
        return f"Repository '{name}' created successfully."
    except Exception as e:
        return f"Exception during create_repo: {str(e)}"