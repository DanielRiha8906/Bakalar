from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional


@tool("add_pull_request_review_comment_to_pending_review")
def add_pull_request_review_comment_to_pending_review_tool(owner: str, repo:str, pullNumber: int, path: str, body: str, subjectType: str, line: Optional[int] = None, startline: Optional[int] = None, side: Optional[str] = None, startSide: Optional[str] = None) -> str:
    """
    Add a comment to the latest pending pull request review using MCP.

    This function adds a comment to a file in a pending pull request review.
    Ensure that a pending review has already been created before calling this.

    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to which the comment applies.
        path (str): The relative path to the file within the repository to comment on.
        body (str): The content of the review comment.
        subjectType (str): The level at which the comment is targeted. Must be "FILE" or "LINE".
        line (int, optional): The line number in the diff that the comment applies to (for single or end line of a multi-line comment).
        startLine (int, optional): The starting line number for a multi-line comment.
        side (str, optional): The side of the diff to comment on. Must be "LEFT" (base) or "RIGHT" (head).
        startSide (str, optional): The starting side of the diff for a multi-line comment. Must be "LEFT" or "RIGHT".

    Raises:
        ValueError: If required parameters are missing or invalid.
    """
    try:
        
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber,
            "path": path,
            "body": body,
            "subjectType": subjectType,
            "side": side,
            "line": line
        }
        if line is not None: 
            payload["line"] = line
        if startline is not None:
            payload["startline"] = startline
        if startSide is not None:
            payload["startSide"] = startSide
        
        result = call_mcp("add_pull_request_review_comment_to_pending_review", payload)
        if "error" in result:
            return f"Failed to add review comment: {result['error']}"

        return f"Review comment added to PR #{pullNumber} on {path}:{line}."

    except Exception as e:
        return f"Exception during add_pull_request_review_comment_to_pending_review: {str(e)}"
