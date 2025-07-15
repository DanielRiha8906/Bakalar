from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("get_issue")
def get_issue_tool(input: str) -> str:
    """
    Get details of a specific issue in a GitHub repository.

    Input format:
    'owner/repo|issue_number'

    Example:
    'DanielRiha8906/testicek|3'
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

        result = call_mcp("get_issue", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        issue = json.loads(text)

        title = issue.get("title", "No title")
        body = issue.get("body", "")
        state = issue.get("state", "unknown")
        url = issue.get("html_url", "")

        return (
            f"Issue #{issue_number} — **{title}**\n"
            f"State: {state}\n"
            f"URL: {url}\n\n"
            f"{body}"
        )

    except Exception as e:
        return f"Exception in get_issue: {str(e)}"
