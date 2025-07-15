from typing import Union
import json
from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool

@tool("list_files")
def get_file_contents_tool(input: str) -> Union[str, list]:
    """
    List files and directories at a specific path in a GitHub repository using MCP.
    Input format: 'owner/repo|branch|[path]'
    Example (root): 'DanielRiha8906/NUM|main|'
    Example (subdir): 'DanielRiha8906/NUM|main|praxe/'
    """
    try:
        parts = input.strip().strip("'").split("|")
        if len(parts) < 2:
            return "Error: Invalid input format. Use 'owner/repo|branch|[path]'"

        repository = parts[0].strip().strip("'").strip()
        branch = parts[1].strip().strip("'").strip()
        path = parts[2].strip().strip("'").strip() if len(parts) > 2 and parts[2].strip() else "/"

        owner, repo = repository.split("/")

        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": branch
        }

        result = call_mcp("get_file_contents", payload)

        if result.get("result", {}).get("isError"):
            content = result["result"].get("content", [])
            if isinstance(content, list) and content:
                return f"Error fetching contents: {content[0].get('text', 'Unknown error')}"
            return "Unknown error while fetching contents."

        raw = result.get("result", {}).get("content", [])
        if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "text" in raw[0]:
            try:
                raw = json.loads(raw[0]["text"])
            except json.JSONDecodeError:
                return f"Invalid JSON in response: {raw[0]['text']}"

        if not isinstance(raw, list):
            return f"Unexpected response format: {raw}"

        return [entry.get("path", "unknown") for entry in raw]

    except Exception as e:
        return f"Exception in get_file_contents: {str(e)}"