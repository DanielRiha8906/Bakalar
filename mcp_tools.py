import os
import json
import uuid
import base64
import requests

from dotenv import load_dotenv
from typing import Union
from pydantic import BaseModel
from langchain.tools import tool

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

    response = requests.post(MCP_URL, json=body, headers=HEADERS)
    response.raise_for_status()
    return response.json()

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

@tool
def get_file(input: str) -> str:
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

@tool
def write_file(input: str) -> str:
    """
    Write or update a file in a GitHub repo using MCP.
    Input format: 'owner/repo|path|branch|content'
    """
    try:
        repository, path, branch, content = input.split("|", 3)
        if "/" not in repository:
            return "Error: Repository must be in format 'owner/repo'"
        owner, repo = repository.split("/")
        
        # Get latest SHA from GitHub (not MCP!)
        sha, _ = get_github_sha_and_content(owner, repo, path, branch)

        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "content": content,
            "message": f"Agent auto-update: {path}",
            "branch": branch
        }
        if sha:
            payload["sha"] = sha

        result = call_mcp("create_or_update_file", payload)
        if "error" in result:
            return f"Write failed: {result['error']}"
        return "File written successfully."
    except Exception as e:
        return f"Exception during write_file: {str(e)}"

@tool()
def get_me(reason: str = "") -> str:
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
    
@tool
def create_repository(input: str) -> str:
    """
    Create a new GitHub repository using MCP.
    Input format: 'repo_name|description|private|autoInit'
    Example: 'my-new-repo|My test repo|true|true'
    """
    try:
        parts = input.split("|")
        name = parts[0]
        description = parts[1] if len(parts) > 1 else ""
        private = parts[2].lower() == "true" if len(parts) > 2 else True
        autoInit = parts[3].lower() == "true" if len(parts) > 3 else True

        payload = {
            "name": name,
            "description": description,
            "private": private,
            "autoInit": autoInit
        }

        result = call_mcp("create_repository", payload)
        if "error" in result:
            return f"Failed to create repo: {result['error']}"
        return f"Repository '{name}' created successfully."
    except Exception as e:
        return f"Exception during create_repo: {str(e)}"

@tool
def create_branch(input: str) -> str:
    """
    Create a new branch in a GitHub repository using MCP.
    Input format: 'owner/repo|new_branch|from_branch'
    Example: 'DanielRiha8906/Test-MCP|feature-branch|main'
    """
    try:
        repo_info = input.split("|")
        if len(repo_info) < 2:
            return "Error: Invalid input. Format: 'owner/repo|new_branch|from_branch'"

        owner, repo = repo_info[0].split("/")
        branch = repo_info[1]
        from_branch = repo_info[2] if len(repo_info) > 2 else "main"

        payload = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "from_branch": from_branch
        }

        result = call_mcp("create_branch", payload)
        if "error" in result:
            return f"Branch creation failed: {result['error']}"
        return f"Branch '{branch}' created from '{from_branch}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during create_branch: {str(e)}"

@tool
def delete_file(input: str) -> str:
    """
    Delete a file from a GitHub repository using MCP.
    Input format: 'owner/repo|path|branch|message'
    Example: 'DanielRiha8906/Test-MCP|README.md|main|Removing obsolete README'
    """
    try:
        parts = input.split("|")
        if len(parts) != 4:
            return "Error: Invalid input. Expected format is 'owner/repo|path|branch|message'"

        owner_repo, path, branch, message = parts
        owner_repo = owner_repo.strip().strip("'").strip('"')
        if "/" not in owner_repo:
            return "Error: owner/repo must be specified like 'DanielRiha8906/testicek'"
        owner, repo = owner_repo.split("/")

        sha, _ = get_github_sha_and_content(owner, repo, path, branch)
        if not sha:
            return f"Error: Could not retrieve SHA for '{path}' in '{owner}/{repo}@{branch}'"

        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "message": message,
            "branch": branch,
            "sha": sha
        }

        result = call_mcp("delete_file", payload)
        if "error" in result:
            return f"File deletion failed: {result['error']}"
        return f"File '{path}' deleted from branch '{branch}' in '{owner}/{repo}'."

    except Exception as e:
        return f"Exception during delete_file: {str(e)}"

@tool
def get_file_contents(input: str) -> Union[str, list]:
    """
    List files and directories at a specific path in a GitHub repository using MCP.
    Input format: 'owner/repo|branch|[path]'
    Example (root): 'DanielRiha8906/NUM|main|'
    Example (subdir): 'DanielRiha8906/NUM|main|praxe/'
    """
    try:
        parts = input.strip().strip("'").split("|")
        if len(parts) < 2:
            return "Error: Invalid input format. Use 'owner/repo|branch|[path]'"

        repository = parts[0].strip().strip("'").strip()
        branch = parts[1].strip().strip("'").strip()
        path = parts[2].strip().strip("'").strip() if len(parts) > 2 and parts[2].strip() else "/"

        owner, repo = repository.split("/")

        payload = {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": branch
        }

        print("\n=== MCP get_file_contents PAYLOAD ===")
        print(json.dumps(payload, indent=2))
        print("======================================")

        result = call_mcp("get_file_contents", payload)

        print("\n=== MCP get_file_contents RESPONSE ===")
        print(json.dumps(result, indent=2))
        print("======================================\n")

        if result.get("result", {}).get("isError"):
            content = result["result"].get("content", [])
            if isinstance(content, list) and content:
                return f"Error fetching contents: {content[0].get('text', 'Unknown error')}"
            return "Unknown error while fetching contents."

        raw = result.get("result", {}).get("content", [])
        if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "text" in raw[0]:
            try:
                raw = json.loads(raw[0]["text"])
            except json.JSONDecodeError:
                return f"Invalid JSON in response: {raw[0]['text']}"

        if not isinstance(raw, list):
            return f"Unexpected response format: {raw}"

        return [entry.get("path", "unknown") for entry in raw]

    except Exception as e:
        return f"Exception in get_file_contents: {str(e)}"

@tool
def push_files(input: str) -> str:
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


@tool
def search_repositories(input: str) -> str:
    """
    Search for GitHub repositories owned by a specific user using MCP.
    Input: GitHub username (e.g., 'DanielRiha8906')
    """
    try:
        query = f"user:{input}"
        payload = {"query": query}

        result = call_mcp("search_repositories", payload)
        
        if isinstance(result, str):
            return f"Unexpected response: {result}"

        if "error" in result:
            return f"Search failed: {result['error']}"

        raw_content = result.get("result", {}).get("content", [])
        if not raw_content:
            return "No repositories found."

        repo_names = []
        for entry in raw_content:
            if isinstance(entry, dict) and "text" in entry:
                try:
                    parsed = json.loads(entry["text"])
                    for repo in parsed.get("items", []):
                        repo_names.append(repo.get("full_name", "unknown"))
                except Exception as parse_error:
                    return f"Error parsing JSON content: {parse_error}"

        return "\n".join(repo_names) if repo_names else "No repositories found."

    except Exception as e:
        return f"Exception during search_repositories: {str(e)}"

@tool
def get_commit(input: str) -> str:
    """
    Get details of a specific commit.
    Input format: 'owner/repo|commit_sha'
    Example: 'DanielRiha8906/NUM|0a67897f767ed0bc9d34b6988392d699f381f03f'
    """
    try:
        repo_info, sha = input.split("|")
        owner, repo = repo_info.split("/")
        payload = {"owner": owner, "repo": repo, "sha": sha}

        result = call_mcp("get_commit", payload)

        #error in call_mcp
        if "error" in result:
            return f"Error: {result['error']}"

        text = result["result"]["content"][0]["text"]
        data = json.loads(text)

        commit = data["commit"]
        msg = commit["message"].strip()
        author = commit["author"]["name"]
        date = commit["author"]["date"]

        return f"{msg}\nBy {author} on {date}"

    # General error
    except Exception as e:
        return f"Exception in get_commit: {str(e)}"


@tool
def list_commits(input: str) -> str:
    """
    List commits in a GitHub repository.
    Input format: 'owner/repo|branch'
    Example: 'DanielRiha8906/Test-MCP|main'
    """
    try:
        repo_info, branch = input.strip().split("|")
        owner, repo = repo_info.strip().strip("'").strip('"').split("/")
        branch = branch.strip().strip("'").strip('"').replace("\n", "").replace("\n", "")


        payload = {
        "owner": owner.strip().strip("'\"`"),
        "repo": repo.strip().strip("'\"`"),
        "sha": branch.strip().strip("'\"`")
        }

        result = call_mcp("list_commits", payload)

        #Error in call_mcp
        if "error" in result:
            return f"Commit list failed: {result['error']}"

        # Error in Json
        if result.get("result", {}).get("isError"):
            raw_content = result["result"].get("content", [])
            if raw_content and isinstance(raw_content[0], dict):
                return f"Commit listing failed: {raw_content[0].get('text', 'Unknown error')}"
            return "Commit listing failed with unknown MCP error."

        # Parse successful response
        content = result.get("result", {}).get("content", [])
        if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
            try:
                parsed = json.loads(content[0]["text"])
                sha_list = []
                for c in parsed:
                    sha = c.get("sha", "")
                    msg = c.get("commit", {}).get("message", "").strip().splitlines()[0]
                    sha_list.append(f"{sha} :: {msg}")

                return "\n".join(sha_list)
            except Exception as e:
                return f"Error parsing commit JSON: {e}"

        return f"Unexpected response format: {content}"

    except Exception as e:
        return f"Exception during list_commits: {str(e)}"

@tool
def list_branches(input: str) -> str:
    """
    List all branches in a GitHub repository using MCP.
    Input format: 'owner/repo'
    Example: 'DanielRiha8906/Test-MCP'
    """
    try:
        owner, repo = input.strip().strip("'\"").split("/")
        repo = repo.strip().strip("'").strip('"').replace("\n", "").replace("\n", "")
        payload = {
            "owner": owner,
            "repo": repo
        }

        print("\n=== MCP REQUEST ===")
        print(f"Tool: list_branches")
        print(json.dumps(payload, indent=2))
        print("===")

        result = call_mcp("list_branches", payload)

        print("\n=== MCP RESPONSE ===")
        print(json.dumps(result, indent=2))
        print("===")

        if "error" in result:
            return f"Branch listing failed: {result['error']}"

        content = result.get("result", {}).get("content", [])
        if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
            try:
                parsed = json.loads(content[0]["text"])
                branches = [entry.get("name", "unknown") for entry in parsed]
                return "\n".join(branches) if branches else "No branches found."
            except Exception as e:
                return f"Error parsing branch list JSON: {e}"

        return f"Unexpected response format: {content}"

    except Exception as e:
        return f"Exception during list_branches: {str(e)}"
     