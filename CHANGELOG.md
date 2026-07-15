# Changelog

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
- docs/DISTANCE_LEARNING.md with full architecture
