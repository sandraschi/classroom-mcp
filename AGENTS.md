# AGENTS.md — classroom-mcp

## Identity

- **Name**: classroom-mcp
- **Purpose**: Student, class, course, and teaching agent management for distance learning
- **Owner**: Sandra Schipal, Vienna
- **Ports**: Backend 11105, Frontend 11106
- **Depends on**: learnbot-mcp (:11101) for lesson content delivery

## Architecture

```
classroom-mcp (management)
  ├── Courses — code, title, subject, level, credits
  ├── Modules — sequenced course units with learning objectives
  ├── Courseware — lectures, readings, problem sets, quizzes per module
  ├── Teaching agents — lecturer, tutor, grader, designer per course
  ├── Students — name, email, token, language, level
  ├── Classes — groups of students with schedule
  ├── Assignments — class + lesson + due date
  └── Progress — scores, time spent, vocab mastery
```

## MCP Tools (45 + 1 prompt + 1 resource)

### Server
- `help`, `status`, `server_shutdown`

### Students
- `student_create`, `student_get`, `student_list`, `student_update`, `student_delete`

### Classes
- `class_create`, `class_list`, `class_get`, `class_add_student`, `class_remove_student`, `class_delete`

### Assignments
- `assignment_create`, `assignment_list`, `assignment_delete`

### Progress
- `progress_record`, `progress_list`

### Courses
- `course_create`, `course_list`, `course_get`, `course_delete`

### Modules
- `module_create`, `module_list`, `module_delete`

### Courseware
- `courseware_create`, `courseware_list`, `courseware_delete`

### Teaching Agents
- `agent_create`, `agent_list`, `agent_delete`

### AI generation
- `syllabus_generate`, `courseware_generate_ai`, `syllabus_list`

### Prompt / resource
- `plan_lesson` prompt, `classroom://status` resource

## Processes (no NSSM service; stdio + REST run separately)

- MCP stdio: `uv run python -m classroom_mcp` (lifespan runs `init_db()`)
- REST daemon: `uv run python -m classroom_mcp.api` → :11105
  (`GET /api/health`, `GET /api/status`, `POST /api/shutdown`)
- Launcher: `.\start.ps1` (clears :11105 zombies, TCP-polls readiness)
- DB: `data/classroom.db` (aiosqlite, WAL) — single writer per process;
  do not run two REST daemons on the same DB file.
- Bridge: learnbot-mcp :11101 via `LEARNBOT_URL` (optional)

## Key Files

| File | Purpose |
|------|---------|
| `src/classroom_mcp/database.py` | Schema + CRUD for all entities |
| `src/classroom_mcp/tools.py` | MCP tool registrations |
| `src/classroom_mcp/api.py` | Starlette REST API |
| `docs/DISTANCE_LEARNING.md` | Full architecture doc |

## Code Rules

- Python 3.12+, async-first, aiosqlite for DB
- FastMCP 3.4+ tool patterns
- pydantic-settings for config
- All CRUD returns dict with `success` bool
- REST API mirrors MCP tools on port 11105
