from ..shared.call_mcp import call_mcp
from langchain.tools import tool
import json

@tool("search_issues")
def search_issues_tool(input: str) -> str:
    """
    Search for issues in GitHub repositories using query syntax.

    Input format:
    'query|owner/repo'

    Example:
    'is:open|DanielRiha8906/testicek'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.strip().split("|")
        if len(parts) < 2:
            return "Invalid input. Format: 'query|owner/repo'"

        query = parts[0].strip().strip("`'\"")  # Clean up quotes and markdown remnants
        owner_repo = parts[1].strip().strip("`'\"")

        if "/" not in owner_repo:
            return "Invalid owner/repo format. Expected 'owner/repo'."

        owner, repo = owner_repo.split("/", 1)

        payload = {
            "query": query,
            "owner": owner,
            "repo": repo
        }

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
