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

def call_mcp(method, params):
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params
    }

    print("\n=== MCP REQUEST ===")
    print("Method:", method)
    print("Params:", params)
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

import base64

@tool
def get_file(input: str) -> str:
    """
    Get a file's content from a GitHub repo.
    Input format: 'owner/repo|path|branch'
    """
    import base64
    try:
        repository, path, branch = input.split("|")
        owner, repo = repository.split("/")
        result = call_mcp("repos.get_file_content", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": branch
        })

        print("\n=== RAW RESULT ===")
        print(result)
        print("==================\n")

        encoded_content = result.get("result", {}).get("content")
        if encoded_content:
            return base64.b64decode(encoded_content).decode("utf-8")
        return "Error: Content missing or empty."
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
        call_mcp("repos.write_file", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "content": encoded_content,
            "branch": branch,
            "commit_message": f"Agent auto-update: {path}"
        })
        return "File updated."
    except Exception as e:
        return f"Error: {str(e)}"