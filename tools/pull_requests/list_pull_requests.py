from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("list_pull_requests")
def list_pull_requests_tool(input: str) -> str:
    """
    List pull requests in a GitHub repository using MCP.
    Input format: owner/repo|[state]|[base]|[head]|[sort]|[direction]|[page]|[perPage]
    Example: 'DanielRiha8906/Test-MCP|open|main|||desc|1|10'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.split("|")
        if len(parts) < 1:
            return "Error: Invalid input. Format: 'owner/repo|[state]|[base]|[head]|[sort]|[direction]|[page]|[perPage]'"

        owner_repo = parts[0].split("/")
        if len(owner_repo) != 2:
            return "Error: Invalid repo identifier. Use format 'owner/repo'."

        payload = {
            "owner": owner_repo[0],
            "repo": owner_repo[1]
        }

        optional_fields = ["state", "base", "head", "sort", "direction", "page", "perPage"]
        for i, key in enumerate(optional_fields, start=1):
            if len(parts) > i and parts[i]:
                if key in ["page", "perPage"]:
                    payload[key] = str(int(parts[i]))
                else:
                    payload[key] = parts[i]

        result = call_mcp("list_pull_requests", payload)
        if "error" in result:
            return f"Listing pull requests failed: {result['error']}"

        return result.get("result", "No pull requests found.")

    except Exception as e:
        return f"Exception during list_pull_requests: {str(e)}"
