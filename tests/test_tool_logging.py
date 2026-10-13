"""Tests for tool_call ring-buffer logging via FastMCP middleware."""

from __future__ import annotations

import pytest
from fastmcp.exceptions import NotFoundError

from classroom_mcp.activity_log import clear_logs, query_logs


@pytest.mark.asyncio
async def test_tool_call_logged_ok() -> None:
    from classroom_mcp.tools import mcp

    clear_logs()
    await mcp.call_tool("status", {})
    result = query_logs(kind="tool_call")
    assert result["total"] >= 1
    entry = result["entries"][0]
    assert entry["level"] == "INFO"
    assert entry["meta"]["tool"] == "status"
    assert "(ok)" in entry["detail"]


@pytest.mark.asyncio
async def test_tool_call_logged_error() -> None:
    from classroom_mcp.tools import mcp

    clear_logs()
    with pytest.raises(NotFoundError):
        await mcp.call_tool("no_such_tool_xyz", {})
    result = query_logs(kind="tool_call")
    assert result["total"] >= 1
    entry = result["entries"][0]
    assert entry["level"] == "ERROR"
    assert "no_such_tool_xyz" in entry["detail"]
