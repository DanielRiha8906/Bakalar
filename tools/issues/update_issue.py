from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json
from typing import Optional

@tool("update_issue")
def update_issue_tool(
    owner: str,
    repo: str,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    assignees: Optional[str] = None,
    labels: Optional[str] = None,
    milestone: Optional[int] = None,
    state: Optional[str] = None
) -> str:
    """
    Update an existing issue in a GitHub repository.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        issue_number: The number of the issue to update.
        title: New title for the issue (optional).
        body: New body for the issue (optional).
        assignees: Comma-separated list of assignees (optional).
        labels: Comma-separated list of labels (optional).
        milestone: New milestone number (optional).
        state: New state for the issue ("open" or "closed", optional).

    Example:
        DanielRiha8906/testicek|1|title=New title;body=Updated description;state=closed;labels=bug,urgent
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number,
            "title": title,
            "body": body,
            "assignees": assignees.split(",") if assignees else None,
            "labels": labels.split(",") if labels else None,
            "milestone": milestone,
            "state": state
        }

        payload = {key: value for key, value in payload.items() if value is not None}

        result = call_mcp("update_issue", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        updated_issue = json.loads(text)

        url = updated_issue.get("html_url", "")
        return f"Issue #{issue_number} updated: {url}"

    except Exception as e:
        return f"Exception in update_issue: {str(e)}"
