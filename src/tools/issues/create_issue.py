from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("create_issue")
def create_issue_tool(owner: str, repo: str, title:str, body:str) -> str:
    """
    Create a new issue in a GitHub repository.

    args:
        owner: The owner of the repository.
        repo: The name of the repository.
        title: The title of the issue.
        body: The body of the issue.
    
    Example:
    'DanielRiha8906/NUM|Bug in login|Clicking login throws an error.'

    
    The issue will be created without assignees, labels, or milestone.
    """
    try:
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
