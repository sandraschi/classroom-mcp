# CLAUDE.md — classroom-mcp

Student, class, course, and teaching-agent management for distance learning.
MCP over stdio (`python -m classroom_mcp`), REST on :11105 (`python -m classroom_mcp.api`).

## Entry points

| Command | What |
|---|---|
| `uv run python -m classroom_mcp` | MCP server (stdio, 45 tools) |
| `uv run python -m classroom_mcp.api` | REST API (:11105, Starlette) |
| `just serve` / `just serve-rest` / `just test` / `just lint` / `just ci` | Shortcuts |
| `.\start.ps1` | Launcher (clears :11105 zombies, waits for TCP ready) |

## Key files

| File | Purpose |
|---|---|
| `src/classroom_mcp/tools.py` | All 45 MCP tools (Annotated params, Return Format/Examples docstrings) |
| `src/classroom_mcp/database.py` | aiosqlite schema + CRUD; upserts narrow `except IntegrityError`, never bare `except Exception` on insert paths |
| `src/classroom_mcp/api.py` | Starlette REST (explicit Tauri origins + Tailscale/LAN regex CORS) |
| `src/classroom_mcp/config.py` | pydantic-settings; `LEARNBOT_URL` default `http://127.0.0.1:11101` |
| `skills/classroom/SKILL.md` | Agent tool-awareness prompt |
| `tests/` | Regression tests (email-upsert collision, learnbot bridge) |

## Standards

- Python 3.12+, `uv run` (never naked `python`), ruff line-length 100, ASCII-only prose (no em dashes).
- Fleet bars: `mcp-central-docs/standards/AGENT_PROTOCOLS.md`; ports in `operations/WEBAPP_PORTS.md` (11105/11106, adjacent, unforbidden).
- Optional bridge: learnbot-mcp on :11101 (`assignment_create_with_lesson`, `syllabus_generate`); server works standalone.
- Webapp not built yet (ports reserved, `web_sota/` is a stub) — see `TODO.md` P1.
