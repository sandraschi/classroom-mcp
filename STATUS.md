# classroom-mcp — Status

**Updated**: 2026-09-28

## Current State

| Area | Status | Notes |
|------|--------|-------|
| Students CRUD | ✅ | Create, list, get, update, delete with active/inactive |
| Classes CRUD | ✅ | Create, list, get, update, delete + add/remove students |
| Assignments | ✅ | Create, list, delete with due dates |
| Progress tracking | ✅ | Record scores, time spent, vocab mastery per student/assignment |
| Courses | ✅ | Create, list, get, update, delete with code, subject, level, credits |
| Modules | ✅ | Create, list, delete with sequence + learning objectives |
| Courseware | ✅ | Create, list, delete — lectures, readings, problem sets, quizzes, projects |
| Teaching agents | ✅ | Create, list, delete — lecturer, tutor, grader, designer per course |
| Human teachers (marketplace) | ✅ | Create, list, get, delete + student referrals with status tracking |
| AI curriculum generation | ✅ | `syllabus_generate`, `courseware_generate_ai` — framework-aware (CEFR, HSK, DELF, DELE, Goethe, JLPT) |
| learnbot-mcp bridge | ✅ | `assignment_create_with_lesson` calls learnbot-mcp's lesson_generate over LEARNBOT_URL |
| REST API | ✅ | All CRUD endpoints on port 11105, CORS, SPA serving |
| MCP tools | ✅ | 45 tools + plan_lesson prompt + classroom://status resource |
| Server ops | ✅ | help, status, server_shutdown; REST /api/status + POST /api/shutdown |
| Repo hygiene | ✅ | start.ps1/bat, CI (ruff/format/pyright/pytest), pre-commit, session files, llms, glama |
| Git | ✅ | Initialized, pushed to GitHub (private) |

## Architecture

```
classroom-mcp (:11105)         learnbot-mcp (:11101)
  Courses                         Personas + chat
  Modules + courseware            Lessons + vocab SR
  Teaching agents                 TTS + robot + emotion
  Human teachers + referrals
  Students + classes
  Assignments + progress
```

## Dependencies

| Service | Port | Required? |
|---------|------|-----------|
| classroom-mcp API | 11105 | — |
| learnbot-mcp | 11101 | Optional (for lesson content via assignment_create_with_lesson) |

## Known gaps

- Webapp not built — `web_sota/` is a stub (no package.json). Roster, courses,
  timetable, progress dashboard still open (see TODO.md P1).
- No portmanteau refactor (45 individual tools) and no stdio→HTTP proxy —
  deferred as breaking/architectural work, not drift.
- Prefab UI (`prefab-ui` dep + `app=True` cards) deferred — package
  unverifiable offline; adding an unresolvable dep would break `uv sync`.
- MCPB pack needs the DXT desktop app or `mcpb` CLI (`just mcpb-pack`
  validates and then reports the manual step).
- No tests — `tests/` is empty. See CHANGELOG 0.2.0 for two bugs (email
  upsert collision, learnbot-mcp bridge port/path) that shipped
  undetected because of this.
- No `README.md`, `glama.json`, or `llms.txt`/`llms-full.txt`.

## What's Next

See [TODO.md](TODO.md). Priority: webapp pages (roster, courses, timetable,
progress dashboard), student-facing view, test coverage.
