from typing import Union, Optional, List, Dict, Any
import base64
import json
import re
from ..shared.call_mcp import call_mcp
from langchain_core.tools import tool

# ---------- Helpers ----------

def _normalize_path(path: Optional[str]) -> str:
    """Treat empty/None as repo root ('/')."""
    if path is None or str(path).strip() == "":
        return "/"
    return path

_REF_SHA = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)

def _normalize_ref(ref: Optional[str]) -> Optional[str]:
    """
    Accepts None, a SHA, 'main', 'heads/main', or 'refs/heads/main'
    Returns None (let server default) or a normalized ref suitable for /git/refs/*
    """
    if ref is None or str(ref).strip() == "":
        return None
    r = ref.strip()
    if _REF_SHA.fullmatch(r):
        return r
    if r.startswith("refs/"):
        return r
    if r.startswith("heads/"):
        return f"refs/{r}"
    return f"refs/heads/{r}"

def _first_text_chunk(content: List[Dict[str, Any]]) -> Optional[str]:
    """First plain text item (status/error messages or directory JSON)."""
    for c in content:
        if isinstance(c, dict) and c.get("type") == "text" and "text" in c:
            return c["text"]
    return None

def _extract_payload_text(content: List[Dict[str, Any]]) -> Optional[str]:
    """
    Prefer resource.text (actual file body). Fall back to a plain text item
    (used by server for directory JSON or status messages).
    """
    # 1) File body lives here in your MCP server responses
    for c in content:
        if isinstance(c, dict) and c.get("type") == "resource":
            r = c.get("resource") or {}
            if isinstance(r, dict) and isinstance(r.get("text"), str):
                return r["text"]
    # 2) Fallback (directory listing JSON string or status message)
    return _first_text_chunk(content)

# ---------- Tool ----------

@tool("get_file_contents")
def get_file_contents_tool(
    owner: str,
    repo: str,
    path: str,
    ref: Optional[str] = None
) -> Union[str, List[str]]:
    """
    Read a file or list a directory at 'path' in a GitHub repo via MCP.

    Returns:
      - str  : the file content (decoded text)
      - list : child paths if 'path' refers to a directory

    Raises:
      RuntimeError on transport/domain errors (surfaceable by ToolNode).
    """
    norm_path = _normalize_path(path)
    norm_ref = _normalize_ref(ref)

    payload: Dict[str, Any] = {"owner": owner, "repo": repo, "path": norm_path}
    if norm_ref is not None:
        payload["ref"] = norm_ref

    result = call_mcp("get_file_contents", payload)

    # Transport error (JSON-RPC)
    if isinstance(result, dict) and "error" in result:
        msg = result["error"].get("message", str(result["error"]))
        raise RuntimeError(f"MCP transport error: {msg}")

    # Normalize shape and pull content array
    is_error = bool(result.get("isError")) or bool(result.get("result", {}).get("isError"))
    content: List[Dict[str, Any]] = result.get("result", {}).get("content", [])

    # Keep a status text to show on errors; prefer payload for actual data
    status_text = _first_text_chunk(content) or ""
    raw = _extract_payload_text(content) or ""

    # Domain-level error from server or textual error flag
    if is_error or "exception" in status_text.lower() or "error" in status_text.lower():
        raise RuntimeError(f"MCP domain error: {status_text or raw or 'unknown error'}")

    # If server gave us a resource.text, it's almost certainly a FILE body → return as-is
    # Otherwise, server likely returned a directory listing JSON in `raw`.
    # Try to parse JSON; if it fails, still return raw (some servers might send files as text).
    parsed: Any
    try:
        parsed = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        # Not JSON → treat as a file text payload
        return raw

    # Directory listing: JSON array
    if isinstance(parsed, list):
        # Prefer extracting `path` fields; fall back to plain strings if provided
        paths: List[str] = []
        for e in parsed:
            if isinstance(e, dict) and "path" in e and isinstance(e["path"], str):
                paths.append(e["path"])
            elif isinstance(e, str):
                paths.append(e)
        if paths:
            return paths
        raise RuntimeError(f"Unexpected directory listing format: {parsed!r}")

    # Some servers might return an object with 'content' (or type=file) in the text JSON.
    if isinstance(parsed, dict):
        if parsed.get("type") == "file":
            content_str = parsed.get("content", "")
            encoding = parsed.get("encoding")
            if encoding == "base64":
                try:
                    return base64.b64decode(content_str).decode("utf-8", errors="replace")
                except Exception:
                    # If decode fails, return raw base64 to avoid data loss
                    return content_str
            return content_str
        if "content" in parsed:
            return parsed["content"]

    # If we got here, `raw` existed but wasn't a list/dict JSON. Return it.
    if isinstance(raw, str) and raw:
        return raw

    # Last resort: surface entire content envelope for debugging
    raise RuntimeError(f"Unexpected response content: {content!r}")
