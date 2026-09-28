# classroom-mcp — Copilot instructions

This repo is classroom-mcp: student/class/course management over MCP (stdio) + REST (:11105).

- Before suggesting IDs, list first: `student_list()`, `class_list()`, `course_list()`.
- New tools follow the file's pattern: `Annotated` params with `Field(description)`,
  `## Return Format` + `## Examples` docstring sections, `{success, message}` returns.
- DB: aiosqlite upserts catch `aiosqlite.IntegrityError` for the update fallback;
  all other exceptions return `{"success": False, "error": ...}` after rollback.
- Run `just ci` before finishing: ruff check, ruff format --check, pytest.
