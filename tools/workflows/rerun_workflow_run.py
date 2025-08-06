from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("rerun_workflow_run")
def rerun_workflow_run_tool(owner: str, repo: str, run_id: int) -> str:
    """
    Re-run an entire GitHub Actions workflow run using MCP.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        run_id (int): The unique identifier of the workflow run to re-run.

    Returns:
        str: Result message or error.

    Example:
        'owner="octocat", repo="Hello-World", run_id=123456789'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "run_id": run_id
        }

        result = call_mcp("rerun_workflow_run", payload)

        if "error" in result:
            return f"Workflow re-run failed: {result['error']}"
        return result.get("result", "Workflow re-run triggered successfully.")

    except Exception as e:
        return f"Exception during rerun_workflow_run: {str(e)}"
