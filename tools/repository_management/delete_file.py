from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
from .get_file import get_github_sha_and_content

@tool("delete_file")
def delete_file_tool(input: str) -> str:
    """
    Delete a file from a GitHub repository using MCP.
    Input format: 'owner/repo|path|branch|message'
    Example: 'DanielRiha8906/Test-MCP|README.md|main|Removing obsolete README'
    """
    try:
        parts = input.split("|")
        if len(parts) != 4:
            return "Error: Invalid input. Expected format is 'owner/repo|path|branch|message'"

        owner_repo, path, branch, message = parts
        owner_repo = owner_repo.strip().strip("'").strip('"')
        if "/" not in owner_repo:
            return "Error: owner/repo must be specified like 'DanielRiha8906/testicek'"
        owner, repo = owner_repo.split("/")

        sha, _ = get_github_sha_and_content(owner, repo, path, branch)
        if not sha:
            return f"Error: Could not retrieve SHA for '{path}' in '{owner}/{repo}@{branch}'"

        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "message": message,
            "branch": branch,
            "sha": sha
        }

        result = call_mcp("delete_file", payload)
        if "error" in result:
            return f"File deletion failed: {result['error']}"
        return f"File '{path}' deleted from branch '{branch}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during delete_file: {str(e)}"