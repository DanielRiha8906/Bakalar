from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("get_issue")
def get_issue_tool(owner: str, repo: str, issue_number: int) -> str:
    """
    Get details of a specific issue in a GitHub repository.

    args: 
        owner: The owner of the repository.
        repo: The name of the repository.
        issue_number: The number of the issue to retrieve.

    Example:
    'DanielRiha8906/testicek|3'
    """
    try:
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
            f"Issue {issue_number} — {title}\n"
            f"State: {state}\n"
            f"URL: {url}\n\n"
            f"{body}"
        )

    except Exception as e:
        return f"Exception in get_issue: {str(e)}"
