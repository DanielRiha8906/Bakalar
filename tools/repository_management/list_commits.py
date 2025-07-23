from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json
from typing import Optional

@tool("list_commits")
def list_commits_tool(owner: str, repo: str, sha: Optional[str] = None, author: Optional[str] = None, perPage: Optional[int] = 10, page: Optional[int] = 1) -> str:
    """
    List all commits in a GitHub repository.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        sha: The SHA of the commit to retrieve (optional).
        author: The author of the commits to filter by (optional).
        perPage: Number of commits to return per page (default is 10).
        page: Page number for pagination (default is 1).

    Example:
        owner: "DanielRiha8906", repo: "testicek", sha: "main", author: "DanielRiha8906", perPage: 5, page: 1
    """
    try:
        payload = {
        "owner": owner,
        "repo": repo,
        "sha": sha,
        "author": author,
        "perPage": perPage,
        "page": page
        }

        payload = {key: value for key, value in payload.items() if value is not None}

        result = call_mcp("list_commits", payload)

        #Error in call_mcp
        if "error" in result:
            return f"Commit list failed: {result['error'].get('message', str(result['error']))}"


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
                for commit in parsed:
                    author = commit.get("commit", {}).get("author", {}).get("name", "unknown")
                    date = commit.get("commit", {}).get("author", {}).get("date", "unknown")
                    commit_sha = commit.get("sha", "")
                    msg = commit.get("commit", {}).get("message", "").strip().splitlines()[0]
                    sha_list.append(f"{commit_sha} - {msg}")

                return "\n".join(sha_list)
            
            except Exception as e:
                return f"Error parsing commit JSON: {e}"

        return f"Unexpected response format: {content}"

    except Exception as e:
        return f"Exception during list_commits: {str(e)}"
