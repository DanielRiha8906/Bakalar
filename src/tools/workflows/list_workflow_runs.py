from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("list_workflow_runs")
def list_workflow_runs_tool(
    owner: str,
    repo: str,
    workflow_id: str,
    ref: Optional[str] = None,
    event: Optional[str] = None,
    status: Optional[str] = None,
    actor: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None
) -> str:
    """
    List GitHub Actions workflow runs for a specific workflow using MCP.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        workflow_id (str): The workflow file name (e.g., 'ci.yml') or ID.
        ref (Optional[str]): Branch or tag to filter runs by.
        event (Optional[str]): GitHub event type that triggered the run (e.g., 'push', 'pull_request').
        status (Optional[str]): Status of the run ('queued', 'in_progress', 'completed', etc.).
        actor (Optional[str]): GitHub username who triggered the workflow.
        page (Optional[int]): Page number for pagination.
        per_page (Optional[int]): Number of results per page.

    Returns:
        str: List of workflow runs or an error message.

    Example:
        'owner="octocat", repo="Hello-World", workflow_id="ci.yml", ref="main"'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "workflow_id": workflow_id
        }

        if ref: payload["ref"] = ref
        if event: payload["event"] = event
        if status: payload["status"] = status
        if actor: payload["actor"] = actor
        if page: payload["page"] = page
        if per_page: payload["per_page"] = per_page

        result = call_mcp("list_workflow_runs", payload)

        if "error" in result:
            return f"Listing workflow runs failed: {result['error']}"
        return result.get("result", "No workflow runs found.")

    except Exception as e:
        return f"Exception during list_workflow_runs: {str(e)}"
