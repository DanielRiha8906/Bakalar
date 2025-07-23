from ..shared.call_mcp import call_mcp
from langchain.tools import tool

@tool("create_pull_request")
def create_pull_request_tool(input: str) -> str:
    """
    Create a new pull request in a GitHub repository using MCP.
    Input format: 'owner/repo|title|head_branch|base_branch|[body]|[draft]'
    Example: 'DanielRiha8906/Test-MCP|Add feature X|feature-x|main|Implements feature X|true'
    """
    try:
        input = input.strip("`'\" \n\r\t")
        parts = input.split("|")
        if len(parts) < 4:
            return "Error: Invalid input. Format: 'owner/repo|title|head_branch|base_branch|[body]|[draft]'"

        owner, repo = parts[0].split("/")
        title = parts[1]
        head = parts[2]
        base = parts[3]
        body = parts[4] if len(parts) > 4 else ""
        draft = parts[5].lower() == "true" if len(parts) > 5 else False

        payload = {
            "owner": owner,
            "repo": repo,
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft
        }

        result = call_mcp("create_pull_request", payload)
        if "error" in result:
            return f"Pull request creation failed: {result['error']}"
        return f"Pull request '{title}' created from '{head}' into '{base}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during create_pull_request: {str(e)}"
