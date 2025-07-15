from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("create_issue")
def create_issue_tool(input: str) -> str:
    """
    Create a new issue in a GitHub repository.

    Input format:
    'owner/repo|title|body'

    Example:
    'DanielRiha8906/NUM|Bug in login|Clicking login throws an error.'

    The issue will be created without assignees, labels, or milestone.
    """
    try:
        parts = input.split("|")
        if len(parts) < 3:
            return "Invalid input. Expected format: 'owner/repo|title|body'"

        owner_repo = parts[0].strip().strip("`'\" ")
        title = parts[1].strip()
        body = "|".join(parts[2:]).strip()
        owner, repo = owner_repo.split("/", 1)

        payload = {
            "owner": owner,
            "repo": repo,
            "title": title,
            "body": body
        }

        result = call_mcp("create_issue", payload)

        if "error" in result:
            return f"Error: {result['error']}"

        text = result["result"]["content"][0]["text"]
        data = json.loads(text)

        issue_number = data.get("number", "unknown")
        issue_url = data.get("html_url", "")

        return f"Issue #{issue_number} created: {issue_url}"

    except Exception as e:
        return f"Exception in create_issue: {str(e)}"
