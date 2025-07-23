from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("update_issue")
def update_issue_tool(input: str) -> str:
    """
    Update an existing issue in a GitHub repository.

    Input format:
    'owner/repo|issue_number|field=value;field=value;...'

    Supported fields: title, body, state (open/closed), assignees (comma-separated), labels (comma-separated)

    Example:
    'DanielRiha8906/testicek|1|title=New title;body=Updated description;state=closed;labels=bug,urgent'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.strip().split("|")
        if len(parts) < 3:
            return "Invalid input. Format: 'owner/repo|issue_number|field=value;...'"

        owner_repo = parts[0].strip().strip("`'\"")
        issue_number = int(parts[1].strip().strip("`'\""))
        field_data = parts[2].strip()

        if "/" not in owner_repo:
            return "Invalid owner/repo format. Expected 'owner/repo'."

        owner, repo = owner_repo.split("/", 1)

        updates = {}
        for pair in field_data.split(";"):
            if "=" not in pair:
                continue
            key, value = pair.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "assignees":
                updates[key] = [x.strip() for x in value.split(",") if x.strip()]
            elif key == "labels":
                updates[key] = [x.strip() for x in value.split(",") if x.strip()]
            elif key == "issue_number":
                continue  # ignore
            else:
                updates[key] = value

        payload = {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number,
            **updates
        }

        result = call_mcp("update_issue", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        updated_issue = json.loads(text)

        url = updated_issue.get("html_url", "")
        return f"Issue #{issue_number} updated: {url}"

    except Exception as e:
        return f"Exception in update_issue: {str(e)}"
