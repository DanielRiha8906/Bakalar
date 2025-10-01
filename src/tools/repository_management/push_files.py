from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
from typing import List, Dict

@tool("push_multiple_files")
def push_files_tool(owner: str, repo: str, branch: str, files: List[Dict[str, str]], message: str) -> str:
    """
    Push multiple files to a GitHub repository using MCP.
    
    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        branch: The branch to push the files to.
        files: A list of dictionaries containing file paths and their content.
        message: The commit message for the file push.
    Returns:
        A message indicating success or failure.
    Raises:
        Exception: If there is an error during the file push operation.
    Example:
        'owner="DanielRiha8906", repo="testicek", branch="main", message="Update files", files=[{"path": "file1.txt", "content": "Content of file 1"}, {"path": "file2.txt", "content": "Content of file 2"}]'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "files": files,
            "message": message
        }

        result = call_mcp("push_files", payload)
        if "error" in result:
            return f"Push failed: {result['error']}"
        return f"Successfully pushed {len(files)} file(s) to {owner}/{repo}@{branch}."

    except Exception as e:
        return f"Exception during push_files: {str(e)}"
