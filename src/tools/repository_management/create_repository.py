from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
from typing import Optional
@tool("create_repository")
def create_repository_tool(name: str, description: Optional[str] = None, private: Optional[bool] = True, autoInit: Optional[bool] = True ) -> str:
    """
    Create a new GitHub repository using MCP.
    
    args:
        name: The name of the repository.
        description: A short description of the repository (optional).
        private: Whether the repository should be private (optional, default is True).
        autoInit: Whether to create an initial commit with an empty README (default is True).

    Example: 'my-new-repo|My test repo|true|true'
    """
    try:
        payload = {
            "name": name,
            "description": description,
            "private": private,
            "autoInit": autoInit
        }

        payload = {key: value for key, value in payload.items() if value is not None}

        result = call_mcp("create_repository", payload)
        if "error" in result:
            return f"Failed to create repo: {result['error']}"
        return f"Repository '{name}' created successfully."
    
    except Exception as e:
        return f"Exception during create_repo: {str(e)}"