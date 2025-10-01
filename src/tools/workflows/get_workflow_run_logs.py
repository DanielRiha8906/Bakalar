from ..shared.call_mcp import call_mcp
from langchain.tools import tool
from typing import Optional

@tool("get_workflow_run_logs")
def get_workflow_run_logs_tool(
    owner: str,
    repo: str,
    run_id: int,
    return_content: bool = True,
    tail_lines: Optional[int] = 500
) -> str:
    """
    Retrieve logs for a specific GitHub Actions workflow run using MCP.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        run_id (int): The unique identifier of the workflow run.
        return_content (bool): If True, return the actual log text instead of just a URL (recommended for LLMs).
        tail_lines (int, Optional): Number of lines to return from the end of the log (default is 500).

    Returns:
        str: The log content or an error message.
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "run_id": run_id,
            "return_content": return_content,
            "tail_lines": tail_lines
        }

        result = call_mcp("get_workflow_run:logs", payload)

        if "error" in result:
            return f"Fetching workflow logs failed: {result['error']}"
        return result.get("result", "Logs retrieved successfully.")

    except Exception as e:
        return f"Exception during get_workflow_run_logs: {str(e)}"
