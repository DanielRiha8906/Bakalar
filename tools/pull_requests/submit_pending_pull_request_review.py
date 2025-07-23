from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("submit_pending_pull_request_review")
def submit_pending_pull_request_review_tool(input: str) -> str:
    """
    Submit the latest pending pull request review using MCP.
    Input format: 'owner/repo|pull_number|event|[body]'
    - event must be one of: APPROVE, REQUEST_CHANGES, COMMENT
    Example: 'DanielRiha8906/Test-MCP|3|APPROVE|Looks good to me!'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.split("|")
        if len(parts) < 3:
            return "Error: Invalid input. Format: 'owner/repo|pull_number|event|[body]'"

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])
        event = parts[2].upper()  # APPROVE, REQUEST_CHANGES, COMMENT

        if event not in {"APPROVE", "REQUEST_CHANGES", "COMMENT"}:
            return "Error: event must be APPROVE, REQUEST_CHANGES, or COMMENT"

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number,
            "event": event,
            "body": parts[3] if len(parts) > 3 else ""
        }

        result = call_mcp("submit_pending_pull_request_review", payload)
        if "error" in result:
            return f"Failed to submit review: {result['error']}"

        return f"Review submitted for PR #{pull_number} in '{owner}/{repo}' with event '{event}'."

    except Exception as e:
        return f"Exception during submit_pending_pull_request_review: {str(e)}"
