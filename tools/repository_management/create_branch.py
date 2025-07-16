from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("create_branch")
def create_branch_tool(input: str) -> str:
    """
    Create a new branch in a GitHub repository using MCP.
    Input format: 'owner/repo|new_branch|from_branch'
    Example: 'DanielRiha8906/Test-MCP|feature-branch|main'
    """
    try:
        repo_info = [part.strip().replace("’", "").replace("‘", "").replace("'", "") for part in input.split("|")]
        if len(repo_info) < 2:
            return "Error: Invalid input. Format: 'owner/repo|new_branch|from_branch'"

        owner_repo = repo_info[0].split("/")
        if len(owner_repo) != 2:
            return "Error: Invalid repo format. Use 'owner/repo'."

        owner, repo = owner_repo[0].strip(), owner_repo[1].strip()
        branch = repo_info[1]
        raw_from_branch = repo_info[2] if len(repo_info) > 2 else "main"

        from_branch = raw_from_branch.strip("`'\" \n\r\t")

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