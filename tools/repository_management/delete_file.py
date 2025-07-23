from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
from .get_file import get_github_sha_and_content

@tool("delete_file")
def delete_file_tool(owner: str, repo: str, path: str, message: str, branch: str) -> str:
    """
    Delete a file from a GitHub repository using MCP.
    args:
        owner: The owner of the repository.
        repo: The name of the repository.
        path: The path to the file in the repository.
        message: The commit message for the file deletion.
        branch: The branch to delete the file from.
    Returns:
        A message indicating success or failure.
    Raises:
        Exception: If there is an error during the file deletion operation.
    Example:
        'DanielRiha8906/testicek|path/to/file.txt|Delete file| Update file content|main'
    """
    try:
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
            return f"File deletion failed: {result['error'].get('message', str(result['error']))}"

        return f"File '{path}' deleted from branch '{branch}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during delete_file: {str(e)}"