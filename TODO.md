# classroom-mcp — TODO

**Updated**: 2026-07-15

## P1 — Webapp

- [ ] **Roster page** — student list with add/edit/deactivate, CSV import
- [ ] **Courses page** — course list, module tree, courseware items per module
- [ ] **Teaching agents page** — assign agents to courses, edit persona prompts
- [ ] **Timetable page** — calendar view with class sessions, assignment due dates
- [ ] **Progress dashboard** — grid of students × assignments with scores, CSV export
- [ ] **Student-facing view** — restricted view showing only own assignments + progress

## P2 — AI Courseware Generation

- [ ] `courseware_generate(course_id, module_id, type, topic)` — LLM produces lecture/reading/problem set from topic
- [ ] `course_generate_syllabus(course_id)` — LLM generates full module list with objectives
- [ ] `agent_generate_lecture(agent_id, module_id)` — teaching agent writes lecture content
- [ ] `agent_generate_quiz(agent_id, module_id, count)` — teaching agent creates quiz questions

## P3 — Grading

- [ ] `assignment_grade(assignment_id, student_id, rubric)` — LLM grades submission against rubric
- [ ] Agent Grader role — auto-grade all submissions for an assignment
- [ ] Gradebook export (CSV, PDF report card)

## P4 — Auth & Multi-tenant

- [ ] Simple token auth for students (no signup, teacher creates account)
- [ ] Student login — sees only their classes and assignments
- [ ] Teacher login — full admin access
- [ ] Billing tier (Stripe) for cloud-hosted instances

## P5 — Courseware Marketplace (future)

- [ ] Courseware export/import between instances
- [ ] Shared courseware depot in mcp-central-docs
- [ ] Rating system for AI-generated courseware quality
