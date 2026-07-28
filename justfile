set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

default: serve

serve:
    uv run python -m classroom_mcp

serve-rest:
    uv run python -m classroom_mcp.api

lint:
    uv run ruff check src/

fmt:
    uv run ruff format src/

test:
    uv run pytest tests/ -q -v

deps:
    uv sync
