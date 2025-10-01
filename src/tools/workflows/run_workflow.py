from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("run_workflow")
def run_workflow_tool(
    owner: str,
    repo: str,
    workflow_id: str,
    ref: str,
    inputs: Optional[dict] = None
) -> str:
    """
    Trigger a GitHub Actions workflow run using MCP.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        workflow_id (str): The workflow file name (e.g. 'ci.yml') or ID.
        ref (str): The git reference for the workflow (branch or tag).
        inputs (Optional[dict]): A dictionary of input parameters for the workflow (if defined in the YAML).

    Returns:
        str: Result message or error.

    Example:
        'owner="octocat", repo="Hello-World", workflow_id="ci.yml", ref="main", inputs={"build": "true"}'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "workflow_id": workflow_id,
            "ref": ref
        }

        if inputs is not None:
            payload["inputs"] = inputs

        result = call_mcp("run_workflow", payload)

        if "error" in result:
            return f"Workflow run failed: {result['error']}"
        return result.get("result", "Workflow triggered successfully.")

    except Exception as e:
        return f"Exception during run_workflow: {str(e)}"
