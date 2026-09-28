# classroom-mcp

Student and class management for the fleet — roster, timetable, courses, courseware, teaching agents, and progress tracking, exposed as 45 MCP tools plus a REST API.

## What's here

| Area | Notes |
|------|-------|
| Students / classes | CRUD, active/inactive status, add/remove students from classes |
| Assignments / progress | Due dates; per-student score, time-spent, and vocab-mastery tracking |
| Courses / modules / courseware | Code, subject, level, credits; sequenced modules with learning objectives; lectures, readings, problem sets, quizzes, projects |
| Teaching agents | Lecturer, tutor, grader, designer roles per course |
| Human teacher marketplace | Teacher records plus student referrals with status tracking |
| AI curriculum generation | `syllabus_generate`, `courseware_generate_ai` — framework-aware (CEFR, HSK, DELF, DELE, Goethe, JLPT) |
| [learnbot-mcp](https://github.com/sandraschi/learnbot-mcp) bridge | `assignment_create_with_lesson` calls learnbot-mcp's lesson generation over `LEARNBOT_URL` (optional — classroom-mcp works standalone) |

REST API on port **11105** (uvicorn/Starlette, CORS enabled, SPA serving). MCP tools run over stdio.

## Status

Two regression tests exist (`tests/test_student_upsert.py`, `tests/test_learnbot_bridge.py`) covering an email-upsert collision bug and a learnbot-mcp bridge port/path bug that both shipped undetected before the tests were written — see `CHANGELOG.md` (0.2.0). Both currently pass. Test coverage beyond those two regressions is thin; most of the 45 tools have no automated test.

See `TODO.md` for what's planned next — webapp pages (roster, courses, timetable, progress dashboard), a student-facing view, and broader test coverage are the open items.

## Quick start

```powershell
cd D:\Dev\repos\classroom-mcp
uv sync
uv run pytest tests\ -q      # 2 files, 6 tests, currently passing
uv run python -m classroom_mcp.tools     # MCP server, stdio
uv run python -m classroom_mcp.api       # REST API, port 11105
```

## Requirements

- Python 3.12+
- FastMCP 3.4+
- SQLite (via `aiosqlite`) — no external database needed

## Architecture

```
classroom-mcp (:11105)         learnbot-mcp (:11101, optional)
  Courses                         Personas + chat
  Modules + courseware            Lessons + vocab spaced repetition
  Teaching agents                 TTS + robot + emotion
  Human teachers + referrals
  Students + classes
  Assignments + progress
```
