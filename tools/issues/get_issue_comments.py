from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("get_issue_comments")
def get_issue_comments_tool(input: str) -> str:
    """
    Get comments for a specific issue in a GitHub repository.

    Input format:
    'owner/repo|issue_number'

    Example:
    'DanielRiha8906/testicek|1'
    """
    try:
        parts = input.strip().split("|")
        if len(parts) != 2:
            return "Invalid input. Expected format: 'owner/repo|issue_number'"

        owner_repo = parts[0].strip()
        issue_number = parts[1].strip()

        if "/" not in owner_repo:
            return "Invalid owner/repo format. Expected 'owner/repo'."

        owner, repo = owner_repo.split("/", 1)

        payload = {
            "owner": owner,
            "repo": repo,
            "issue_number": int(issue_number)
        }

        result = call_mcp("get_issue_comments", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        comments = json.loads(text)

        if not comments:
            return f"Issue #{issue_number} has no comments."

        output = []
        for comment in comments:
            user = comment["user"]["login"]
            body = comment.get("body", "")
            url = comment.get("html_url", "")
            output.append(f"- {user} commented: \"{body}\"\n  {url}")

        return "\n".join(output)

    except Exception as e:
        return f"Exception in get_issue_comments: {str(e)}"
