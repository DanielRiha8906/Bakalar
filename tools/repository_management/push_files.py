from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool


@tool("push_multiple_files")
def push_files_tool(input: str) -> str:
    """
    Push multiple files to a GitHub repository using MCP.
    Input format: 'owner/repo|branch|message|[path1]:::<content1>###path2:::<content2>###...'
    Delimiters:
        - Use '###' to separate multiple files
        - Use ':::' to separate file path and its content
    Example:
        'DanielRiha8906/Test-MCP|main|Initial commit|README.md:::Hello World!###src/main.py:::print("Hello")'
    """
    try:
        repo_info, branch, message, files_blob = input.split("|", 3)
        owner, repo = repo_info.split("/")

        files_raw = files_blob.split("###")
        files = []
        for f in files_raw:
            if ":::" not in f:
                return f"Error: Invalid file entry '{f}'. Expected format: path:::content"
            path, content = f.split(":::", 1)
            files.append({
                "path": path.strip(),
                "content": content
            })

        payload = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "message": message,
            "files": files
        }

        result = call_mcp("push_files", payload)
        if "error" in result:
            return f"Push failed: {result['error']}"
        return f"Successfully pushed {len(files)} file(s) to {owner}/{repo}@{branch}."

    except ValueError:
        return "Error: Input must contain exactly four parts separated by '|'"
    except Exception as e:
        return f"Exception during push_files: {str(e)}"
