from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json
from typing import Optional

@tool("get_commit_details")
def get_commit_tool(owner: str, repo: str, sha: str, page: Optional[int] = 10, perPage: Optional[int] = 1) -> str:
    """
    Get all details of a specific commit.
    Input format: 'owner/repo|commit_sha'
    args:
        owner: The owner of the repository.
        repo: The name of the repository.
        sha: The SHA of the commit to retrieve.
        page: The page number for pagination (default is 10).
        perPage: Number of commits per page (default is 1).

    Example: 'DanielRiha8906/NUM|0a67897f767ed0bc9d34b6988392d699f381f03f'
    """
    try:
        payload = {"owner": owner,
                   "repo": repo,
                   "sha": sha,
                   "page": page,
                   "perPage": perPage}
        payload = {key: value for key, value in payload.items() if value is not None}

        result = call_mcp("get_commit", payload)

        if "error" in result:
            return f"Get commit failed: {result['error'].get('message', str(result['error']))}"

        text = result["result"]["content"][0]["text"]
        data = json.loads(text)

        commit = data.get("commit", {})
        msg = commit.get("message", "").strip()
        author = commit.get("author", {}).get("name", "Unknown")
        date = commit.get("author", {}).get("date", "Unknown")

        file_changes = []
        for file in data.get("files", []):
            fname = file.get("filename", "unknown")
            status = file.get("status", "unknown")
            additions = file.get("additions", 0)
            deletions = file.get("deletions", 0)
            changes = file.get("changes", 0)
            file_changes.append(f"- {fname} ({status}): +{additions} / -{deletions} (total changes: {changes})")

        files_output = "\n".join(file_changes) if file_changes else "No files changed."

        return f"{msg}\nBy {author} on {date}\n\nChanged files:\n{files_output}"

    except Exception as e:
        return f"Exception in get_commit: {str(e)}"
