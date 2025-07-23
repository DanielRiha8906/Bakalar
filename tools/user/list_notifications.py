from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json
from typing import Optional

@tool("list_notifications")
def list_notifications_tool(
    owner: Optional[str] = None,
    repo: Optional[str] = None,
    page: Optional[int] = 1,
    perPage: Optional[int] = 10,
    filter: Optional[str] = "default",
    since: Optional[str] = None,
    before: Optional[str] = None
) -> str:
    """
    List GitHub notifications for the authenticated user.
    Args:
        owner: The owner of the repository (optional).
        repo: The name of the repository (optional).
        page: Page number for pagination (default is 1).
        perPage: Number of notifications to return per page (default is 10).
        filter: Filter for notifications (default is "default").
        since: Only show notifications updated after this time (optional).
        before: Only show notifications updated before this time (optional).
    Example:
        'owner=DanielRiha8906;repo=testicek;filter=include_read_notifications;since=2023-01-01;before=2023-12-31;page=1;perPage=10'
    Returns:
        A string listing notifications in the format:
        "repo: subject — reason (updated at time)"
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "page": page,
            "perPage": perPage,
            "filter": filter,
            "since": since,
            "before": before
        }

        payload = {key: value for key, value in payload.items() if value is not None}

        result = call_mcp("list_notifications", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        content = result["result"]["content"]
        if not content:
            return "No notifications found."

        notifications = json.loads(content[0]["text"])
        if not notifications:
            return "No notifications found."

        lines = []
        for notif in notifications[:10]:  # Show only first 10
            repo = notif.get("repository", {}).get("full_name", "[unknown repo]")
            subject = notif.get("subject", {}).get("title", "[no title]")
            reason = notif.get("reason", "[no reason]")
            updated_at = notif.get("updated_at", "unknown time")
            lines.append(f"{repo}: {subject} — {reason} (updated at {updated_at})")

        return "\n".join(lines)

    except Exception as e:
        return f"Exception in list_notifications: {str(e)}"
