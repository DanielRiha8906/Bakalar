from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("add_issue_comment")
def add_issue_comment_tool(owner: str, repo: str, issue_number: str, comment_body:str) -> str:
    """
    Add a comment to a specific GitHub issue.

    args:
        owner: The owner of the repository.
        repo: The name of the repository.
        issue_number: The number of the issue to comment on.
        comment_body: The body of the comment to add.

    Example:
    'DanielRiha8906/testicek|1|Thanks for the update, looks good!'
    """
    try:

        payload = {
            "owner": owner,
            "repo": repo,
            "issue_number": str(issue_number),
            "body": comment_body
        }

        result = call_mcp("add_issue_comment", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        comment = json.loads(text)

        url = comment.get("html_url", "")
        return f"Comment added: {url}"

    except Exception as e:
        return f"Exception in add_issue_comment: {str(e)}"
