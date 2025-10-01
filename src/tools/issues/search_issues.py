from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json
from typing import Optional

@tool("search_issues")
def search_issues_tool(query: str, owner: Optional[str] = None, repo: Optional[str] = None, sort: Optional[str] = None, order: Optional[str] = None, page: int = 1, perPage: int = 30
) -> str:
    """
    Search for issues in GitHub repositories using query syntax.

    args:
        query: The search query string.
        owner: Optional owner of the repository to limit search.
        repo: Optional repository name to limit search.
        sort: Optional field to sort results by (e.g., "created", "updated", "comments").
        order: Optional order of results ("asc" or "desc").
        page: Page number for pagination (default is 1).
        perPage: Number of results per page (default is 30).
    Example:
    search_issues("bug fix", owner="DanielRiha8906", repo="testicek")

    """
    try:
        payload = {
            "query": query,
            "owner": owner,
            "repo": repo,
            "sort": sort,
            "order": order,
            "page": page,
            "perPage": perPage
        }

        payload = {key: value for key, value in payload.items() if value is not None}

        result = call_mcp("search_issues", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        issues = json.loads(text).get("items", [])

        if not issues:
            return "No issues found."

        output = "\n".join(
        f"#{issue['number']}: {issue['title']} — {issue['html_url']}"
        for issue in issues[:5])

        return json.dumps(output)

    except Exception as e:
        return f"Exception in search_issues: {str(e)}"
