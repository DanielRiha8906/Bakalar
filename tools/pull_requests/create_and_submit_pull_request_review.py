from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("create_and_submit_pull_request_review")
def create_and_submit_pull_request_review_tool(owner: str, repo: str, pullNumber: int, body: str, event: str, commitID: Optional[str] = None) -> str:
    """
    Create and submit a pull request review without comments using MCP.
    
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to review.
        body (str): The content of the review.
        event (str): The type of review event. Must be "APPROVE", "REQUEST_CHANGES", or "COMMENT".
        commitID (str, optional): The commit ID to associate with the review. If not provided, the latest commit will be used.    

    Raises:
        ValueError: If the event type is not one of the allowed values.
        Exception: If there is an error during the MCP call.
    """
    try:
        if event not in {"APPROVE", "REQUEST_CHANGES", "COMMENT"}:
            return "Error: event must be APPROVE, REQUEST_CHANGES, or COMMENT"

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber,
            "event": event,
            "commitID": commitID,
            "body": body
        }
        if commitID is not None:
            payload["commitID"] = commitID
        result = call_mcp("create_and_submit_pull_request_review", payload)
        if "error" in result:
            return f"Failed to create and submit review: {result['error']}"

        return f"Review submitted for PR #{pullNumber} in '{owner}/{repo}' with event '{event}'."

    except Exception as e:
        return f"Exception during create_and_submit_pull_request_review: {str(e)}"
