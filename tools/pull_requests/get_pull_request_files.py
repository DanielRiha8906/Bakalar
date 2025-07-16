from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_pull_request_files")
def get_pull_request_files_tool(input: str) -> str:
    """
    Get the list of files changed in a specific pull request using MCP.
    Input format: 'owner/repo|pull_number|[page]|[perPage]'
    Example: 'DanielRiha8906/Test-MCP|3|1|30'
    """
    try:
        parts = input.split("|")
        if len(parts) < 2:
            return "Error: Invalid input. Format: 'owner/repo|pull_number|[page]|[perPage]'"

        owner, repo = parts[0].split("/")
        pull_number = int(parts[1])

        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pull_number
        }

        if len(parts) > 2 and parts[2]:
            payload["page"] = int(parts[2])
        if len(parts) > 3 and parts[3]:
            payload["perPage"] = int(parts[3])

        result = call_mcp("get_pull_request_files", payload)
        if "error" in result:
            return f"Get pull request files failed: {result['error']}"

        return result.get("result", "No files found.")

    except Exception as e:
        return f"Exception during get_pull_request_files: {str(e)}"
