import requests
import os
import base64
from langchain.tools import tool

def get_github_sha_and_content(owner, repo, path, branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_OAUTH_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and data.get("type") == "file":
            sha = data.get("sha", "")
            content_b64 = data.get("content", "")
            try:
                content = base64.b64decode(content_b64).decode("utf-8") if content_b64 else ""
            except Exception as decode_error:
                return "", f"[decode error]: {decode_error}"
            return sha, content
        else:
            return "", f"Path '{path}' is not a file."
    return "", f"[{response.status_code}] {response.text}"


file_cache = {}

@tool("get_file")
def get_file_tool(input: str) -> str:
    """
    Get a file's content from a GitHub repo.
    Input format: 'owner/repo|path|branch'
    """
    try:
        repository, path, branch = input.split("|")
        owner, repo = repository.split("/")

        sha, content = get_github_sha_and_content(owner, repo, path, branch)
        file_cache[f"{owner}/{repo}/{path}"] = {
            "content": content,
            "sha": sha
        }

        return content if content and not content.startswith("[") else f"Error: {content}"
    except Exception as e:
        return f"Error: {str(e)}"