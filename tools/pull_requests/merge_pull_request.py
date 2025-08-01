from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("merge_pull_request")
def merge_pull_request_tool(owner: str, repo: str, pullNumber: int, commit_title: Optional[str] = None, commit_message: Optional[str] = None, merge_method: Optional[str] = "merge" ) -> str:
    """
    Merge a pull request in a GitHub repository using MCP.
    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to merge.
        commit_title (Optional[str]): The title for the merge commit.
        commit_message (Optional[str]): The message for the merge commit.
        merge_method (Optional[str]): The method to use for merging (merge, squash, rebase), base is merge.
    Returns:
        str: A message indicating the result of the merge operation or an error message.
    
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }
        if commit_title: payload["commit_title"] = commit_title
        if commit_message: payload["commit_message"] = commit_message
        if merge_method: payload["merge_method"] = merge_method


        result = call_mcp("merge_pull_request", payload)
        if "error" in result:
            return f"Merge failed: {result['error']}"

        return f"Pull request #{pullNumber} in '{owner}/{repo}' merged successfully."

    except Exception as e:
        return f"Exception during merge_pull_request: {str(e)}"
