from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("cancel_workflow_run")
def cancel_workflow_run_tool(owner: str, repo: str, run_id: int) -> str:
    """
    Cancel an in-progress GitHub Actions workflow run using MCP.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        run_id (int): The unique identifier of the workflow run to cancel.

    Returns:
        str: Result message or error.

    Example:
        'owner="octocat", repo="Hello-World", run_id=987654321'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "run_id": run_id
        }

        result = call_mcp("cancel_workflow_run", payload)

        if "error" in result:
            return f"Workflow cancellation failed: {result['error']}"
        return result.get("result", "Workflow run cancelled successfully.")

    except Exception as e:
        return f"Exception during cancel_workflow_run: {str(e)}"
