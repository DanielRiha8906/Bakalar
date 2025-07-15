from tools.shared.call_mcp import call_mcp
from langchain_core.tools import tool

@tool("get_me")
def get_me_tool(reason: str = "") -> str:
    """
    Get details of the authenticated GitHub user. Use this when a request includes "me", "my".
    The output will not change unless the user updates their GitHub profile.
    """
    try:
        result = call_mcp("get_me", {"reason": reason} if reason else {})
        if "error" in result:
            return f"Failed to get user: {result['error']}"
        return f"GitHub user info:\n{result['result']}"
    except Exception as e:
        return f"Exception while calling get_me: {str(e)}"