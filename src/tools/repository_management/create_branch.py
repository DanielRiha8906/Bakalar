import json
from langchain.tools import tool
from ..shared.call_mcp import call_mcp
from typing import Optional

@tool("create_branch")
def create_branch_tool(owner: str, repo: str, branch: str, from_branch: Optional[str] = None) -> str:
    """
    Create a new branch in a GitHub repository using MCP.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        branch: The name of the new branch to create.
        from_branch: The branch to base the new branch on (default is "main").
    
    Example: 'DanielRiha8906/Test-MCP|feature-branch|main'
    """
    try:
        if from_branch is None:
            from_branch = "main"
        payload = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "from_branch": from_branch
        }

        result = call_mcp("create_branch", payload)        
        
        if "error" in result:
            return f"Branch creation failed: {result['error']}"
        return f"Branch '{branch}' created from '{from_branch}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during create_branch: {str(e)}"