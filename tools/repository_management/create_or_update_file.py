from langchain_core.tools import tool
from ..shared.call_mcp import call_mcp
from .get_file import get_github_sha_and_content

@tool("create_or_update_file")
def write_file_tool(input: str) -> str:
    """
    Write or update a file in a GitHub repo using MCP.
    Input format: 'owner/repo|path|branch|content'
    """
    try:
        repository, path, branch, content = input.split("|", 3)
        if "/" not in repository:
            return "Error: Repository must be in format 'owner/repo'"
        owner, repo = repository.split("/")
        
        # Get latest SHA from GitHub (not MCP!)
        sha, _ = get_github_sha_and_content(owner, repo, path, branch)

        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "content": content,
            "message": f"Agent auto-update: {path}",
            "branch": branch
        }
        if sha:
            payload["sha"] = sha

        result = call_mcp("create_or_update_file", payload)
        if "error" in result:
            return f"Write failed: {result['error']}"
        return "File written successfully."
    except Exception as e:
        return f"Exception during write_file: {str(e)}"