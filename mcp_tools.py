import base64
from langchain.tools import tool
import uuid
import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

MCP_URL = "https://api.githubcopilot.com/mcp/"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('GITHUB_OAUTH_TOKEN')}",
    "Content-Type": "application/json"
}

def call_mcp(tool_name, arguments):
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    print("\n=== MCP REQUEST ===")
    print("Tool:", tool_name)
    print("Arguments:", arguments)
    print("===================\n")

    response = requests.post(MCP_URL, json=body, headers=HEADERS)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("\n=== MCP ERROR RESPONSE ===")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("==========================\n")
        raise e

    return response.json()


class GetFileInput(BaseModel):
    repository: str
    path: str
    branch: str


@tool
def get_file(input: str) -> str:
    """
    Get a file's content from a GitHub repo.
    Input format: 'owner/repo|path|branch'
    """
    try:
        repository, path, branch = input.split("|")
        owner, repo = repository.split("/")

        result = call_mcp("get_file_contents", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": branch
        })

        print("\n=== RAW RESULT ===")
        print(result)
        print("==================\n")

        content_arr = result.get("result", {}).get("content", [])
        if content_arr and isinstance(content_arr, list):
            text_b64 = content_arr[0].get("text", "")
            return base64.b64decode(text_b64).decode("utf-8")
        return "Error: Content missing or improperly formatted."
    except Exception as e:
        return f"Error: {str(e)}"



class WriteFileInput(BaseModel):
    repository: str
    path: str
    content: str
    branch: str

@tool
def write_file(input: str) -> str:
    """
    Write or update a file in a GitHub repo.
    Input format: 'owner/repo|path|branch|content'
    """
    try:
        repository, path, branch, content = input.split("|", 3)
        owner, repo = repository.split("/")
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        sha = ""
        try:
            get_result = call_mcp("get_file_contents", {
                "owner": owner,
                "repo": repo,
                "path": path,
                "ref": branch
            })
            text_b64 = get_result.get("result", {}).get("content", [])[0].get("text", "")
            decoded = base64.b64decode(text_b64).decode("utf-8")
            sha = get_result.get("result", {}).get("sha", "")
        except Exception:
            pass 

        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "content": encoded_content,
            "message": f"Agent auto-update: {path}",
            "branch": branch
        }

        if sha:
            payload["sha"] = sha

        result = call_mcp("create_or_update_file", payload)

        return "File written successfully."
    except Exception as e:
        return f"Error: {str(e)}"
