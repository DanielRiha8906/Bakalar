from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("get_workflow_run_usage")
def get_workflow_run_usage_tool(owner: str, repo: str, run_id: int) -> str:
    """
    Retrieve GitHub Actions usage metrics for a specific workflow run using MCP.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        run_id (int): The unique identifier of the workflow run.

    Returns:
        str: Usage details or an error message.

    Example:
        'owner="octocat", repo="Hello-World", run_id=246813579'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "run_id": run_id
        }

        result = call_mcp("get_workflow_run_usage", payload)

        if "error" in result:
            return f"Fetching workflow usage failed: {result['error']}"
        return result.get("result", "Usage details retrieved successfully.")

    except Exception as e:
        return f"Exception during get_workflow_run_usage: {str(e)}"
