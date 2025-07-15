from ..shared.call_mcp import call_mcp
import json
from langchain.tools import tool

@tool("list_issues")
def list_issues_tool(input: str) -> str:
    """
    List issues in a GitHub repository.

    Input format:
    'owner/repo|[state=open|closed|all]|[labels=label1,label2]'

    Example:
    'DanielRiha8906/testicek|state=open|labels=bug,urgent'

    You can omit filters to list all open issues:
    'DanielRiha8906/testicek'
    """
    try:
        parts = input.strip().replace("\n", "").replace("\r", "").strip("`'\" ").split("|")

        if len(parts) < 1:
            return "Invalid input. Format: 'owner/repo|[filters]'"

        owner_repo = parts[0].strip().strip("`'\"")
        if "/" not in owner_repo:
            return "Invalid owner/repo format. Expected 'owner/repo'."
        owner, repo = owner_repo.split("/", 1)

        payload = {
            "owner": owner,
            "repo": repo,
            "perPage": 10,  # default page size
            "page": 1       # always first page unless expanded later
        }

        for part in parts[1:]:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "labels":
                payload[key] = [label.strip() for label in value.split(",")]
            elif key in ["state", "sort", "direction"]:
                payload[key] = value

        result = call_mcp("list_issues", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        issues = json.loads(text)

        if not issues:
            return "No issues found."

        return "\n".join(
            f"#{issue['number']}: {issue['title']} ({issue['state']}) — {issue['html_url']}"
            for issue in issues[:10]
        )

    except Exception as e:
        return f"Exception in list_issues: {str(e)}"
