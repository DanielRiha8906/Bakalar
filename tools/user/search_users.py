from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool
import json

@tool("search_users")
def search_users_tool(input: str) -> str:
    """
    Search for GitHub users using MCP.

    Input format:
    'query=search_term;sort=followers;order=desc;page=1;perPage=5'

    Only 'query' is required. Sort can be 'followers', 'repositories', or 'joined'.
    """
    try:
        # Clean and parse input
        cleaned_input = input.strip().replace("\n", "").replace("\r", "").strip("`'\" ")
        entries = cleaned_input.split(";")
        parts = dict(entry.split("=", 1) for entry in entries if "=" in entry)

        if "query" not in parts:
            return "Missing required 'query' parameter."

        payload = {
            "query": parts["query"].strip()
        }

        if "sort" in parts:
            payload["sort"] = parts["sort"].strip()
        if "order" in parts:
            payload["order"] = parts["order"].strip()
        if "page" in parts:
            payload["page"] = str(int(parts["page"]))
        if "perPage" in parts:
            payload["perPage"] = str(int(parts["perPage"]))


        result = call_mcp("search_users", payload)

        if "error" in result:
            return f"Error: {result['error']['message']}"

        text = result["result"]["content"][0]["text"]
        data = json.loads(text)
        users = data.get("items", [])

        if not users:
            return "No users found."

        return "\n".join([
            f"{user['login']} — {user.get('profile_url', '[no url]')}"
            for user in users[:5]
        ])

    except Exception as e:
        return f"Exception in search_users: {str(e)}"
