from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_pull_request_reviews")
def get_pull_request_reviews_tool(input: str) -> str:
    """
    Get the list of reviews for a specific pull request using MCP.
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

        result = call_mcp("get_pull_request_reviews", payload)
        if "error" in result:
            return f"Get pull request reviews failed: {result['error']}"

        return result.get("result", "No reviews found.")

    except Exception as e:
        return f"Exception during get_pull_request_reviews: {str(e)}"
