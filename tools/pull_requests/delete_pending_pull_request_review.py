from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("delete_pending_pull_request_review")
def delete_pending_pull_request_review_tool(input: str) -> str:
    """
    Delete the latest pending pull request review using MCP.
    Input format: 'owner/repo|pull_number'
    Example: 'DanielRiha8906/Test-MCP|3'
    """
    try:
        parts = input.split("|")
        if len(parts) != 2:
            return "Error: Invalid input. Format: 'owner/repo|pull_number'"

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number
        }

        result = call_mcp("delete_pending_pull_request_review", payload)
        if "error" in result:
            return f"Failed to delete pending review: {result['error']}"

        return f"Pending review for PR #{pull_number} in '{owner}/{repo}' was deleted."

    except Exception as e:
        return f"Exception during delete_pending_pull_request_review: {str(e)}"
