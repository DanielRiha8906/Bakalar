from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("add_issue_comment")
def add_issue_comment_tool(input: str) -> str:
    """
    Add a comment to a specific GitHub issue.

    Input format:
    'owner/repo|issue_number|comment_body'

    Example:
    'DanielRiha8906/testicek|1|Thanks for the update, looks good!'
    """
    try:
        parts = input.strip().split("|")
        if len(parts) < 3:
            return "Invalid input. Format: 'owner/repo|issue_number|comment_body'"

        owner_repo = parts[0].strip().strip("`'\" ")
        issue_number = parts[1].strip().strip("`'\" ")
        comment_body = "|".join(parts[2:]).strip()

        if "/" not in owner_repo:
            return "Invalid owner/repo format. Expected 'owner/repo'."

        owner, repo = owner_repo.split("/", 1)

        payload = {
            "owner": owner,
            "repo": repo,
            "issue_number": int(issue_number),
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
