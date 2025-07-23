from langchain_core.tools import tool
from ..shared.call_mcp import call_mcp
from .get_file import get_github_sha_and_content

@tool("create_or_update_file")
def write_file_tool(input: str) -> str:
    """
    Write or update a file in a GitHub repo using MCP.
    Input format: 'owner/repo|path|branch|content'
    Example: 'DanielRiha8906/testicek|app.py|main|print("Hello World")'
    """
    try:
        parts = input.split("|", 3)
        if len(parts) != 4:
            return "Error: Invalid input. Format: 'owner/repo|path|branch|content'"

        #forgot to clean input whoops
        repository = parts[0].strip().strip("'\"")
        path = parts[1].strip()
        branch = parts[2].strip()
        content = parts[3].strip().encode("utf-8").decode("unicode_escape")


        if "/" not in repository:
            return "Error: Repository must be in format 'owner/repo'"
        owner, repo = [s.strip().replace("’", "").replace("‘", "").replace("'", "") for s in repository.split("/")]

        sha, _ = get_github_sha_and_content(owner, repo, path, branch)
        if content[-1] == "'":
            content = content[:-1]
        if content.endswith("```"):
            content = content[:-3]
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
        return f"File '{path}' written successfully to branch '{branch}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during write_file: {str(e)}"
