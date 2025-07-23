from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_pull_request_diff")
def get_pull_request_diff_tool(input: str) -> str:
    """
    Get the diff of a specific pull request from a GitHub repository using MCP.
    Input format: 'owner/repo|pull_number'
    Example: 'DanielRiha8906/Test-MCP|3'
    """
    try:
        input = input.strip("`'\" \n\r\t")
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

        result = call_mcp("get_pull_request_diff", payload)
        if "error" in result:
            return f"Get pull request diff failed: {result['error']}"

        return result.get("result", "No diff returned.")

    except Exception as e:
        return f"Exception during get_pull_request_diff: {str(e)}"
