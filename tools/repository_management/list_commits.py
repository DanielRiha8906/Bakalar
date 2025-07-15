from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json

@tool("list_commits")
def list_commits_tool(input: str) -> str:
    """
    List commits in a GitHub repository.
    Input format: 'owner/repo|branch'
    Example: 'DanielRiha8906/Test-MCP|main'
    """
    try:
        repo_info, branch = input.strip().split("|")
        owner, repo = repo_info.strip().strip("'").strip('"').split("/")
        branch = branch.strip().strip("'").strip('"').replace("\n", "").replace("\n", "")


        payload = {
        "owner": owner.strip().strip("'\"`"),
        "repo": repo.strip().strip("'\"`"),
        "sha": branch.strip().strip("'\"`")
        }

        result = call_mcp("list_commits", payload)

        #Error in call_mcp
        if "error" in result:
            return f"Commit list failed: {result['error']}"

        # Error in Json
        if result.get("result", {}).get("isError"):
            raw_content = result["result"].get("content", [])
            if raw_content and isinstance(raw_content[0], dict):
                return f"Commit listing failed: {raw_content[0].get('text', 'Unknown error')}"
            return "Commit listing failed with unknown MCP error."

        # Parse successful response
        content = result.get("result", {}).get("content", [])
        if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
            try:
                parsed = json.loads(content[0]["text"])
                sha_list = []
                for c in parsed:
                    sha = c.get("sha", "")
                    msg = c.get("commit", {}).get("message", "").strip().splitlines()[0]
                    sha_list.append(f"{sha} :: {msg}")

                return "\n".join(sha_list)
            except Exception as e:
                return f"Error parsing commit JSON: {e}"

        return f"Unexpected response format: {content}"

    except Exception as e:
        return f"Exception during list_commits: {str(e)}"
