from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_pull_request_status")
def get_pull_request_status_tool(input: str) -> str:
    """
    Get the status checks of a pull request using MCP.
    Input format: 'owner/repo|pull_number'
    Example: 'DanielRiha8906/Test-MCP|3'
    """
    try:
        parts = input.split("|")
        if len(parts) != 2:
            return "Error: Invalid input. Format: 'owner/repo|pull_number'"

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number
        }

        result = call_mcp("get_pull_request_status", payload)
        if "error" in result:
            return f"Failed to get PR status: {result['error']}"

        return result.get("result", "No status found.")

    except Exception as e:
        return f"Exception during get_pull_request_status: {str(e)}"
