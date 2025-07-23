from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("create_and_submit_pull_request_review")
def create_and_submit_pull_request_review_tool(input: str) -> str:
    """
    Create and submit a pull request review without comments using MCP.
    Input format: 'owner/repo|pull_number|event|commit_sha|[body]'
    - event must be one of: APPROVE, REQUEST_CHANGES, COMMENT
    Example: 'DanielRiha8906/Test-MCP|3|APPROVE|abc123def456|Looks great!'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.split("|")
        if len(parts) < 4:
            return ("Error: Invalid input. Format: 'owner/repo|pull_number|event|commit_sha|[body]'")

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])
        event = parts[2].upper()
        commit_id = parts[3]
        body = parts[4] if len(parts) > 4 else ""

        if event not in {"APPROVE", "REQUEST_CHANGES", "COMMENT"}:
            return "Error: event must be APPROVE, REQUEST_CHANGES, or COMMENT"

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number,
            "event": event,
            "commitID": commit_id,
            "body": body
        }

        result = call_mcp("create_and_submit_pull_request_review", payload)
        if "error" in result:
            return f"Failed to create and submit review: {result['error']}"

        return f"Review submitted for PR #{pull_number} in '{owner}/{repo}' with event '{event}'."

    except Exception as e:
        return f"Exception during create_and_submit_pull_request_review: {str(e)}"
