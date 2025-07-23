from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("update_pull_request")
def update_pull_request_tool(input: str) -> str:
    """
    Update an existing pull request in a GitHub repository using MCP.
    Input format: 'owner/repo|pull_number|[title]|[body]|[base]|[state]|[maintainer_can_modify]'
    Example: 'DanielRiha8906/Test-MCP|3|New title|Updated PR body|main|open|true'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.split("|")
        if len(parts) < 2:
            return "Error: Invalid input. Format: 'owner/repo|pull_number|[title]|[body]|[base]|[state]|[maintainer_can_modify]'"

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number
        }

        if len(parts) > 2 and parts[2]:
            payload["title"] = parts[2]
        if len(parts) > 3 and parts[3]:
            payload["body"] = parts[3]
        if len(parts) > 4 and parts[4]:
            payload["base"] = parts[4]
        if len(parts) > 5 and parts[5]:
            payload["state"] = parts[5]  # should be 'open' or 'closed'
        if len(parts) > 6 and parts[6]:
            payload["maintainer_can_modify"] = parts[6].lower() == "true"

        result = call_mcp("update_pull_request", payload)
        if "error" in result:
            return f"Update pull request failed: {result['error']}"

        return f"Pull request #{pull_number} in '{owner}/{repo}' updated successfully."

    except Exception as e:
        return f"Exception during update_pull_request: {str(e)}"
