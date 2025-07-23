from ..shared.call_mcp import call_mcp
import json
from langchain.tools import tool

@tool("list_issues")
def list_issues_tool(
    owner: str,
    repo: str,
    direction: str = "desc",
    labels: list[str] = [],
    perPage: int = 30,
    page: int = 1,
    sort: str = "created",
    state: str = "open"
) -> str:
    """
    List issues in a GitHub repository.

    args:
        owner (str): Repository owner
        repo (str): Repository name
        direction (str): Sort direction ("asc" or "desc")
        labels (list[str]): Filter by labels
        perPage (int): Results per page (min 1, max 100)
        page (int): Page number for pagination (min 1)
        sort (str): Sort by field ("created", "updated", "comments")
        state (str): Filter by issue state ("open", "closed", "all")
    
    Example:
    'DanielRiha8906/testicek|state=open|labels=bug,urgent'

    You can omit filters to list all open issues:
    'DanielRiha8906/testicek'
    """
    try:
        payload = {
        "owner": owner,
        "repo": repo,
        "direction": direction,
        "labels": labels,
        "perPage": perPage,
        "page": page,
        "sort": sort,
        "state": state
        }

        result = call_mcp("list_issues", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        issues = json.loads(text)

        if not issues:
            return "No issues found."

        return "\n".join(
            f"{issue['number']}: {issue['title']} ({issue['state']}) — {issue['html_url']}"
            for issue in issues[:10]
        )

    except Exception as e:
        return f"Exception in list_issues: {str(e)}"
