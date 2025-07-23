from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("add_pull_request_review_comment_to_pending_review")
def add_pull_request_review_comment_to_pending_review_tool(input: str) -> str:
    """
    Add a comment to the pending pull request review using MCP.
    Input format: 'owner/repo|pull_number|path|body|subjectType|side|line|[startSide]|[startLine]'
    Example (single-line): 'DanielRiha8906/Test-MCP|3|src/main.py|Fix this bug|LINE|RIGHT|42'
    Example (multi-line): 'DanielRiha8906/Test-MCP|3|src/main.py|Refactor this block|LINE|RIGHT|44|RIGHT|40'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.split("|")
        if len(parts) < 7:
            return ("Error: Invalid input. Format: "
                    "'owner/repo|pull_number|path|body|subjectType|side|line|[startSide]|[startLine]'")

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])
        path = parts[2]
        body = parts[3]
        subject_type = parts[4]  # "LINE" or "FILE"
        side = parts[5]          # "LEFT" or "RIGHT"
        line = int(parts[6].strip("` \n\r\t"))

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number,
            "path": path,
            "body": body,
            "subjectType": subject_type,
            "side": side,
            "line": line
        }

        if len(parts) > 7 and parts[7]:
            payload["startSide"] = parts[7]
        if len(parts) > 8 and parts[8]:
           payload["startLine"] = int(parts[8].strip("` \n\r\t"))

        result = call_mcp("add_pull_request_review_comment_to_pending_review", payload)
        if "error" in result:
            return f"Failed to add review comment: {result['error']}"

        return f"Review comment added to PR #{pull_number} on {path}:{line}."

    except Exception as e:
        return f"Exception during add_pull_request_review_comment_to_pending_review: {str(e)}"
