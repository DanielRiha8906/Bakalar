def call_mcp(tool_name: str, arguments: dict):
    import subprocess
    import uuid
    import json
    import os

    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    env = os.environ.copy()
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    wd = os.getenv("github_mcp_server_location", "")
    env["GITHUB_PERSONAL_ACCESS_TOKEN"] = token

    print("\n=== DEBUG: CALLING MCP ===")
    print("Tool name:", tool_name)
    print("Arguments:", json.dumps(arguments, indent=2))
    print("GITHUB_TOKEN (first 8 chars):", token[:8] + "..." if token else "[MISSING]")
    print("===========================\n")

    proc = subprocess.Popen(
        ["go", "run", "cmd/github-mcp-server/main.go", "stdio", "--toolsets=all"],
        cwd=wd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    banner = proc.stderr.readline()
    print("[MCP BANNER]", banner.strip())

    input_payload = json.dumps(body)
    print("[MCP SEND]", input_payload)

    proc.stdin.write(input_payload + "\n")
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
