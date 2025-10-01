from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("get_pull_request_files")
def get_pull_request_files_tool(owner: str, repo: str, pullNumber: int, page: Optional[int] = 1, perPage: Optional[int] = 20 ) -> str:
    """
    Get the list of files changed in a specific pull request using MCP.
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to get the files for.
        page (int, optional): The page number for pagination. Defaults to 5.
        perPage (int, optional): The number of files per page. Defaults to 20
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }
        if page is not None:
            payload["page"] = page
        if perPage is not None:
            payload["perPage"] = perPage
        
        result = call_mcp("get_pull_request_files", payload)
        if "error" in result:
            return f"Get pull request files failed: {result['error']}"

        return result.get("result", "No files found.")

    except Exception as e:
        return f"Exception during get_pull_request_files: {str(e)}"
