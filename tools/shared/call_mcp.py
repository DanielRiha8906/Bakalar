import requests
import uuid
import json
import os
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "Authorization": f"Bearer {os.getenv('GITHUB_OAUTH_TOKEN')}",
    "Content-Type": "application/json"
}

def call_mcp(tool_name: str, arguments: dict):
    import subprocess
    import uuid
    import json

    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    proc = subprocess.Popen(
        ["go", "run", "cmd/github-mcp-server/main.go", "stdio", "--toolsets=all"],
        cwd="/home/aerceas/Documents/baka/github-mcp-server",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    banner = proc.stderr.readline()
    print("[MCP BANNER]", banner.strip())

    proc.stdin.write(json.dumps(body) + "\n")
    proc.stdin.flush()

    response_line = proc.stdout.readline()
    print("[MCP RESPONSE]", response_line.strip())

    try:
        result = json.loads(response_line)

        if "error" in result:
            raise Exception(f"MCP JSON-RPC error: {json.dumps(result['error'])}")

        mcp_result = result.get("result", {})
        if mcp_result.get("isError"):
            raise Exception(f"MCP call failed: {json.dumps(mcp_result.get('content', ''))}")

        return result

    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {e}\nRaw line: {response_line.strip()}")
