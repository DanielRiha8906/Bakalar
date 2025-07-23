from typing import Union, Optional
import json
from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool

@tool("get_file_contents")
def get_file_contents_tool(owner: str, repo: str, path: str, ref: Optional[str] = None) -> Union[str, list]:
    """
    List files and directories at a specific path in a GitHub repository using MCP.
    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        path: The path to the directory or file in the repository.
        ref: The branch or commit SHA to list files from (optional).
    Returns:
        A list of file paths if the path is a directory, or the content of the file if the path is a file.
    Raises:
        Exception: If there is an error during the file retrieval operation.
    Example (root directory):
    'owner="DanielRiha8906", repo="testicek", path="", ref="main"'

    Example (subdirectory):
    'owner="DanielRiha8906", repo="testicek", path="src/", ref="main"'
    """
    try:
        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": ref
        }
        payload = {key: value for key, value in payload.items() if value is not None}

        result = call_mcp("get_file_contents", payload)

        if "error" in result:
            return f"Failed to fetch file list: {result['error'].get('message', str(result['error']))}"


        content = result.get("result", {}).get("content", [])
        if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
            try:
                parsed = json.loads(content[0]["text"])
            except json.JSONDecodeError:
                return f"Invalid JSON in response: {content[0]['text']}"

            if isinstance(parsed, list):
                return [entry["path"] for entry in parsed if "path" in entry]
            elif isinstance(parsed, dict) and parsed.get("type") == "file":
                return parsed.get("content", "[no content]")
            else:
                return f"Unexpected parsed content format: {parsed}"

        return f"Unexpected response content: {content}"

    except Exception as e:
        return f"Exception in get_file_contents_tool: {str(e)}"
