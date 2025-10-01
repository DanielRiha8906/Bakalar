from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("submit_pending_pull_request_review")
def submit_pending_pull_request_review_tool(owner: str, repo: str, pullNumber: int, event: str, body: Optional[str]) -> str:
    """
    Submit the latest pending pull request review using MCP.
    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to review.
        event (str): The event type for the review (APPROVE, REQUEST_CHANGES, COMMENT).
        body (Optional[str]): The body of the review comment. Required for COMMENT event.
    Returns:
        str: A message indicating the result of the review submission or an error message.
    """
    try:
        if event not in {"APPROVE", "REQUEST_CHANGES", "COMMENT"}:
            return "Error: event must be APPROVE, REQUEST_CHANGES, or COMMENT"

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber,
            "event": event
        }
        if body is not None:
            payload["body"] = body 

        result = call_mcp("submit_pending_pull_request_review", payload)
        if "error" in result:
            return f"Failed to submit review: {result['error']}"

        return f"Review submitted for PR #{pullNumber} in '{owner}/{repo}' with event '{event}'."

    except Exception as e:
        return f"Exception during submit_pending_pull_request_review: {str(e)}"
