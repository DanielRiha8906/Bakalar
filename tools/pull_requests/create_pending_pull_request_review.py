from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("create_pending_pull_request_review")
def create_pending_pull_request_review_tool(input: str) -> str:
    """
    Create a pending review for a pull request using MCP.
    Input format: 'owner/repo|pull_number|commit_sha'
    Example: 'DanielRiha8906/Test-MCP|3|abc123def456...'
    """
    try:
        parts = input.split("|")
        if len(parts) != 3:
            return "Error: Invalid input. Format: 'owner/repo|pull_number|commit_sha'"

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])
        commit_id = parts[2]

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number,
            "commitID": commit_id
        }

        result = call_mcp("create_pending_pull_request_review", payload)
        if "error" in result:
            return f"Failed to create pending review: {result['error']}"

        return f"Pending review created for PR #{pull_number} on commit {commit_id}."

    except Exception as e:
        return f"Exception during create_pending_pull_request_review: {str(e)}"
