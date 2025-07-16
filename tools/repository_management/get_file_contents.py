from typing import Union
import json
from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool

@tool("get_file_contents")
def get_file_contents_tool(input: str) -> Union[str, list]:
    """
    List files and directories at a specific path in a GitHub repository using MCP.
    Input format: 'owner/repo|branch|[path]'
    Example (root): 'DanielRiha8906/testicek|main|'
    Example (subdir): 'DanielRiha8906/testicek|main|src/'
    """
    try:
        # Parse and clean parts
        parts = input.strip().strip("'\"").split("|")
        

        repository = parts[0].strip()
        branch = parts[1].strip()
        
        raw_path = parts[2].strip() if len(parts) > 2 else ""
        path = raw_path.strip("`'\" \n\r\t")
        if path in ("", ".", "./"):
            path = "/"

        if "/" not in repository:
            return "Error: Repository must be in format 'owner/repo'"

        # Sanitize owner/repo
        owner, repo = [
            part.strip().replace("’", "").replace("‘", "").replace("'", "").replace("`", "")
            for part in repository.split("/")
        ]

        # Prepare payload for GitHub MCP
        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": f"refs/heads/{branch}" if branch else "",
        }

        print("\n=== MCP CHAGNE THIS YOU WANKER PAYLOAD ===")
        print(json.dumps(payload, indent=2))
        print("======================================")

        result = call_mcp("get_file_contents", payload)

        print("\n=== MCP get_file_contents RESPONSE ===")
        print(json.dumps(result, indent=2))
        print("======================================\n")

        if "error" in result:
            return f"Failed to fetch file list: {result['error']}"

        content = result.get("result", {}).get("content", [])
        if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
            try:
                parsed = json.loads(content[0]["text"])
            except json.JSONDecodeError:
                return f"Invalid JSON in response: {content[0]['text']}"

            if isinstance(parsed, list):
                return [entry.get("path", "unknown") for entry in parsed]
            elif isinstance(parsed, dict) and parsed.get("type") == "file":
                return [parsed.get("path", "unknown")]
            else:
                return f"Unexpected parsed content format: {parsed}"

        return f"Unexpected response content: {content}"

    except Exception as e:
        return f"Exception in get_file_contents_tool: {str(e)}"
