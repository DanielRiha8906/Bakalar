from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_pull_request_reviews")
def get_pull_request_reviews_tool(owner: str, repo: str, pullNumber: int) -> str:
    """
    Get the list of reviews for a specific pull request using MCP.
    Args:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        pullNumber (int): The number of the pull request to get the reviews for.
    Example: 'owner = DanielRiha8906', 'repo = Test-MCP', 'pullNumber = 3'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "pullNumber": pullNumber
        }

        result = call_mcp("get_pull_request_reviews", payload)
        if "error" in result:
            return f"Get pull request reviews failed: {result['error']}"

        return result.get("result", "No reviews found.")

    except Exception as e:
        return f"Exception during get_pull_request_reviews: {str(e)}"
