from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json

@tool("list_notifications")
def list_notifications_tool(input: str = "") -> str:
    """
    List GitHub notifications for the authenticated user.

    Optional input format:
    'filter=default;owner=DanielRiha8906;repo=NSQL_tweeter;since=2025-07-01;before=2025-07-15;page=1;perPage=5
'

    Available filters:
    - filter: default | include_read_notifications | only_participating
    - owner and repo (together): to filter notifications by repo
    - since / before: ISO 8601 timestamps
    - page, perPage: pagination options
    """
    try:
        cleaned_input = input.strip().replace("\n", "").replace("\r", "").strip("`'\" ")
        payload = {}

        if cleaned_input:
            entries = cleaned_input.split(";")
            parts = dict(entry.split("=", 1) for entry in entries if "=" in entry)

            if "filter" in parts:
                payload["filter"] = parts["filter"].strip()
            if "owner" in parts:
                payload["owner"] = parts["owner"].strip()
            if "repo" in parts:
                payload["repo"] = parts["repo"].strip()
            if "since" in parts:
                payload["since"] = parts["since"].strip()
            if "before" in parts:
                payload["before"] = parts["before"].strip()
            if "page" in parts:
                payload["page"] = str(int(parts["page"]))
            if "perPage" in parts:
                payload["perPage"] = str(int(parts["perPage"]))

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
