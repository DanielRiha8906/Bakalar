from tools.shared.call_mcp import call_mcp
from langchain_core.tools import tool
from typing import Optional

@tool("get_me")
def get_me_tool(reason: Optional[str] = None) -> str:
    """
    Get details of the authenticated GitHub user. Use this when a request includes "me", "my".
    The output will not change unless the user updates their GitHub profile.
    Args:
        reason: Optional reason for the request, can be used to provide context.
    
    Example: 
        'me' or 'my profile'
    
    Returns:
        A string containing the user's GitHub profile information.
    
    Raises:
        Exception: If there is an error during the request.
    """
    try:
        result = call_mcp("get_me", {"reason": reason} if reason else {})
        if "error" in result:
            return f"Failed to get user: {result['error']}"
        return f"GitHub user info:\n{result['result']}"
    except Exception as e:
        return f"Exception while calling get_me: {str(e)}"