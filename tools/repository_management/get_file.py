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
    print(f"Fetching file from URL: {url}")
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            print(f"File SHA: {data.get('sha')}")
            print(f"Content snippet (base64): {data.get('content', '')[:30]}...")

            if isinstance(data, dict) and data.get("type") == "file":
                sha = data.get("sha", "")
                content_b64 = data.get("content", "")
                try:
                    content = base64.b64decode(content_b64).decode("utf-8") if content_b64 else ""
                except Exception as decode_error:
                    print(f"Decoding error: {decode_error}")
                    return "", f"[decode error]: {decode_error}"
                return sha, content
            else:
                print("Warning: Path exists but is not a file.")
                return "", f"Path '{path}' is not a file."
        else:
            print(f"Error: [{response.status_code}] {response.text}")
            return "", f"[{response.status_code}] {response.text}"
    except Exception as e:
        print(f"Unhandled exception: {e}")
        return "", f"[exception] {e}"

file_cache = {}

@tool("get_file")
def get_file_tool(owner: str, repo: str, path: str, branch: str) -> str:
    """
    Get a file's content from a GitHub repo.
    args:
        owner: The owner of the repository.
        repo: The name of the repository.
        path: The path to the file in the repository.
        branch: The branch to get the file from.
    Returns:
        The content of the file or an error message.
    Raises:
        Exception: If there is an error during the file retrieval operation.
    Example:
        'owner="DanielRiha8906", repo="testicek", path="src/main.py", branch="main"'
    """
    try:
        if not path.strip():
            return "Error: Path cannot be empty."
        
        sha, content = get_github_sha_and_content(owner, repo, path.strip(), branch.strip())

        cache_key = f"{owner}/{repo}/{path}"
        file_cache[cache_key] = {"content": content, "sha": sha}

        return content if content and not content.startswith("[") else f"Error: {content}"
    except Exception as e:
        return f"Error: {str(e)}"
