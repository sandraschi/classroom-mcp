# Changelog

## [0.2.1] — 2026-09-28 (assfix)

### Added
- `help`, `status`, `server_shutdown` MCP tools; `plan_lesson` prompt;
  `classroom://status` resource.
- `GET /api/status`, `POST /api/shutdown` REST endpoints.
- `start.ps1`/`start.bat` launcher; `.github/workflows/ci.yml`
  (ruff, format check, pyright, pytest); `.pre-commit-config.yaml`;
  session-injection files (`.cursorrules`, `.windsurfrules`, copilot
  instructions, Claude plugin + hooks, opencode/antigravity skills).
- `llms.txt`/`llms-full.txt`, `glama.json`, `manifest.json`, `CLAUDE.md`,
  `renovate.json`, `skills/classroom/SKILL.md`, `just ci` + `just mcpb-pack`.
- Coverage gate (`--cov-fail-under=30`, actual 38%) via pytest-cov;
  `T20` (no-print) ruff rule with test/script exemptions.

### Fixed
- `.env.example` `LEARNBOT_URL` still pointed at port 11104 (fixed to 11101).
- `agent_upsert` narrowed to `except aiosqlite.IntegrityError` for the
  update fallback; other errors roll back and return `success: False`.
- `_version.py` synced to 0.2.0; removed bogus `Connection.daemon`
  assignment; typed the Starlette route list (pyright clean).
- All 45 tools now use `Annotated[..., Field(...)]` params with
  `## Return Format` / `## Examples` docstrings and dialogic messages.

## [0.2.0] — 2026-07-16

### Added
- `student_update`, `class_update`, `course_update` — update-by-ID tools.
  Previously only create/upsert-by-natural-key existed, so fixing a typo in
  a student's name or a course's title meant delete-and-recreate, which
  lost every FK relationship (assignments, progress, modules) pointing at
  that row.
- Human Teachers in the Loop: `human_teacher_create/list/get/delete`,
  `referral_create/list/update_status` — the marketplace concept from
  learnbot-mcp's `docs/DISTANCE_LEARNING.md`, now implemented.
- `syllabus_generate`, `courseware_generate_ai` — AI-generated curriculum
  content per course, framework-aware (CEFR, HSK, DELF, DELE, Goethe, JLPT).
- `framework` field on students/classes.
- `assignment_create_with_lesson` — bridges to learnbot-mcp's
  `lesson_generate` via `LEARNBOT_URL` to back an assignment with real
  lesson content.

### Fixed
- `student_upsert` / `human_teacher_upsert` — blank email defaulted to
  `""`, which collides under the `email` column's `UNIQUE` constraint.
  Creating a second student/teacher with no email silently overwrote the
  first one's data instead of creating a new row. Now stores `NULL` for a
  blank email (SQLite treats `NULL` as always-distinct under `UNIQUE`,
  unlike `""`).
- `human_teacher_upsert`'s bare `except Exception` around the update
  fallback narrowed to `except aiosqlite.IntegrityError` — a real error in
  that path was previously reported back as success.
- `assignment_create_with_lesson` was broken by two independent bugs:
  `LEARNBOT_URL` defaulted to port `11104`, but learnbot-mcp actually runs
  on `11101`; and the request path was `/api/lessons/generate` (plural)
  against a route that's actually `/api/lesson/generate` (singular). Both
  fixed. Also fixed: the call used to treat "learnbot unreachable" and
  "lesson generation failed" the same as "no lesson attached," creating
  the assignment anyway and reporting `success: True`. Now it returns
  `success: False` with a specific error (unreachable / HTTP error /
  learnbot-reported failure) and does not create the assignment at all if
  lesson generation fails — since the tool's whole contract is "assignment
  WITH lesson," a bare assignment isn't what was asked for.

### Corrected
- The `[0.1.0]` entry below claimed this repo added
  `docs/DISTANCE_LEARNING.md`. That file lives in learnbot-mcp, not here —
  removed the claim rather than leave a changelog asserting a file exists
  that doesn't.

## [0.1.0] — 2026-07-15

### Added
- Student CRUD — create, list, get, delete with active/inactive status
- Class CRUD — create, list, get, delete with add/remove student
- Assignment CRUD — create, list, delete with due dates and max score
- Progress tracking — record scores, time spent, vocab mastery
- Course CRUD — create, list, get, delete with code, subject, level, credits
- Module CRUD — create, list, delete with sequence and learning objectives
- Courseware CRUD — create, list, delete with type (lecture, reading, problem_set, quiz, project) and source tracking
- Teaching agent CRUD — create, list, delete with role (lecturer, tutor, grader, designer)
- 28 MCP tools covering all entities
- REST API on port 11105 with CORS and SPA serving
- FastMCP 3.4+ stdio transport
- SQLite persistence (aiosqlite, WAL mode)
- AGENTS.md, .env.example, justfile, CI config
