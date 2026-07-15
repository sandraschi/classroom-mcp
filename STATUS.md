# classroom-mcp — Status

**Updated**: 2026-07-15

## Current State

| Area | Status | Notes |
|------|--------|-------|
| Students CRUD | ✅ | Create, list, get, delete with active/inactive |
| Classes CRUD | ✅ | Create, list, get, delete + add/remove students |
| Assignments | ✅ | Create, list, delete with due dates |
| Progress tracking | ✅ | Record scores, time spent, vocab mastery per student/assignment |
| Courses | ✅ | Create, list, get, delete with code, subject, level, credits |
| Modules | ✅ | Create, list, delete with sequence + learning objectives |
| Courseware | ✅ | Create, list, delete — lectures, readings, problem sets, quizzes, projects |
| Teaching agents | ✅ | Create, list, delete — lecturer, tutor, grader, designer per course |
| REST API | ✅ | All CRUD endpoints on port 11105, CORS, SPA serving |
| MCP tools | ✅ | 28 tools covering all entities |
| Git | ✅ | Initialized, pushed to GitHub (private) |

## Architecture

```
classroom-mcp (:11105)         learnbot-mcp (:11104)
  Courses                         Personas + chat
  Modules + courseware            Lessons + vocab SR
  Teaching agents                 TTS + robot + emotion
  Students + classes
  Assignments + progress
  Timetable + grading
```

## Dependencies

| Service | Port | Required? |
|---------|------|-----------|
| classroom-mcp API | 11105 | — |
| learnbot-mcp | 11104 | Optional (for lesson content) |

## What's Next

See [TODO.md](TODO.md). Priority: webapp pages (roster, courses, timetable, progress dashboard),
AI courseware generation (lecture writer, problem set generator), student-facing view.
