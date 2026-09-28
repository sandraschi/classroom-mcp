---
name: classroom
description: Manage students, classes, courses, assignments and progress in classroom-mcp. Use when enrolling students, building timetables, generating syllabi, or tracking scores.
---

# Classroom skill

## Session Context (classroom-mcp)

Before starting work: call `status()` for health, then `student_list()` /
`class_list()` / `course_list()` to ground IDs. Never invent student, class,
or course IDs — list first.

At end of work: `progress_record()` for graded work; summarize counts.

## Tool map (45 tools)

- Students: `student_create`, `student_get`, `student_list`, `student_update`, `student_delete`
- Classes: `class_create`, `class_list`, `class_get`, `class_update`, `class_add_student`, `class_remove_student`, `class_delete`
- Assignments: `assignment_create`, `assignment_list`, `assignment_delete`, `assignment_create_with_lesson`
- Progress: `progress_record`, `progress_list`
- Courses/modules/courseware: `course_*`, `module_*`, `courseware_*`, `syllabus_generate`, `courseware_generate_ai`, `syllabus_list`
- Teaching agents + human teachers + referrals: `agent_*`, `human_teacher_*`, `referral_*`
- Server: `help`, `status`, `server_shutdown`

REST mirrors this on :11105 (`/api/health`, `/api/status`, `/api/students`, ...).
Learnbot bridge (`assignment_create_with_lesson`, `syllabus_generate`) needs
learnbot-mcp on :11101 via `LEARNBOT_URL`.
