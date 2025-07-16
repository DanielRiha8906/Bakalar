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

    print("===== DEBUG: GitHub API File Request =====")
    print(f"URL: {url}")
    print(f"Owner: {owner}, Repo: {repo}, Path: {path}, Branch: {branch}")
    print(f"Headers: {headers}")
    print("==========================================")

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
def get_file_tool(input: str) -> str:
    """
    Get a file's content from a GitHub repo.
    Input format: 'owner/repo|path|branch'
    """
    try:
        print(f"get_file_tool input: {input}")
        repository, path, branch = input.split("|")
        owner, repo = repository.split("/")
        owner = owner.strip("`'\" \n\r\t")
        repo = repo.strip("`'\" \n\r\t")
        path = path.strip("`'\" \n\r\t")
        branch = branch.strip().strip("`'\" \n\r\t")

        sha, content = get_github_sha_and_content(owner, repo, path.strip(), branch.strip())

        cache_key = f"{owner}/{repo}/{path}"
        file_cache[cache_key] = {"content": content, "sha": sha}

        return content if content and not content.startswith("[") else f"Error: {content}"
    except Exception as e:
        return f"Error: {str(e)}"
