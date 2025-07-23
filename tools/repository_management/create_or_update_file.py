from langchain_core.tools import tool
from ..shared.call_mcp import call_mcp
from .get_file import get_github_sha_and_content

@tool("create_or_update_file")
def write_file_tool(owner: str, repo: str, path: str, branch: str, content: str, message: str) -> str:
    """
    Write or update a file in a GitHub repo using MCP.
    args:
        owner: The owner of the repository.
        repo: The name of the repository.
        path: The path to the file in the repository.
        branch: The branch to write the file to.
        content: The content of the file to write.
        message: The commit message for the file write.
    Returns:
        A message indicating success or failure.
    Raises:
        Exception: If there is an error during the file write operation.

    """
    try:
        sha, _ = get_github_sha_and_content(owner, repo, path, branch)
        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "content": content,
            "message": message,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha

        result = call_mcp("create_or_update_file", payload)
        if "error" in result:
            return f"Write failed: {result['error']}"
        return f"File '{path}' written successfully to branch '{branch}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during write_file: {str(e)}"
