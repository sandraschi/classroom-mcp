"""MCP tools - student, class, assignment, progress management."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Annotated, Any

from fastmcp import Context
from fastmcp.server.lifespan import lifespan
from fastmcp.server.server import FastMCP
from pydantic import Field

from classroom_mcp._version import __version__
from classroom_mcp.config import get_settings
from classroom_mcp.database import (
    agent_delete as _del_agent,
)
from classroom_mcp.database import (
    agent_list as _list_agents,
)
from classroom_mcp.database import (
    agent_upsert as _upsert_agent,
)
from classroom_mcp.database import (
    assignment_create as _create_a,
)
from classroom_mcp.database import (
    assignment_delete as _delete_a,
)
from classroom_mcp.database import (
    assignment_list as _list_a,
)
from classroom_mcp.database import (
    class_add_student as _add_s,
)
from classroom_mcp.database import (
    class_delete as _delete_c,
)
from classroom_mcp.database import (
    class_get as _get_c,
)
from classroom_mcp.database import (
    class_list as _list_c,
)
from classroom_mcp.database import (
    class_remove_student as _remove_s,
)
from classroom_mcp.database import (
    class_update as _update_c,
)
from classroom_mcp.database import (
    class_upsert as _upsert_c,
)
from classroom_mcp.database import (
    course_delete as _del_course,
)
from classroom_mcp.database import (
    course_get as _get_course,
)
from classroom_mcp.database import (
    course_list as _list_courses,
)
from classroom_mcp.database import (
    course_update as _update_course,
)
from classroom_mcp.database import (
    course_upsert as _upsert_course,
)
from classroom_mcp.database import (
    courseware_create as _create_cw,
)
from classroom_mcp.database import (
    courseware_delete as _del_cw,
)
from classroom_mcp.database import (
    courseware_list as _list_cw,
)
from classroom_mcp.database import (
    human_teacher_delete as _del_ht,
)
from classroom_mcp.database import (
    human_teacher_get as _get_ht,
)
from classroom_mcp.database import (
    human_teacher_list as _list_ht,
)
from classroom_mcp.database import (
    human_teacher_upsert as _upsert_ht,
)
from classroom_mcp.database import (
    init_db,
)
from classroom_mcp.database import (
    module_create as _create_mod,
)
from classroom_mcp.database import (
    module_delete as _del_mod,
)
from classroom_mcp.database import (
    module_list as _list_mods,
)
from classroom_mcp.database import (
    progress_list as _list_p,
)
from classroom_mcp.database import (
    progress_upsert as _upsert_p,
)
from classroom_mcp.database import (
    referral_create as _create_ref,
)
from classroom_mcp.database import (
    referral_list as _list_refs,
)
from classroom_mcp.database import (
    referral_update_status as _update_ref,
)
from classroom_mcp.database import (
    student_delete as _delete_s,
)
from classroom_mcp.database import (
    student_get as _get_s,
)
from classroom_mcp.database import (
    student_list as _list_s,
)
from classroom_mcp.database import (
    student_update as _update_s,
)
from classroom_mcp.database import (
    student_upsert as _upsert_s,
)

log = logging.getLogger(__name__)
cfg = get_settings()

_READ_ONLY = {"readonly": True}
_MUTATING: dict = {}


def _error_response(message: str, exc: Exception | None = None) -> dict:
    """Build a dialogic error dict and log the traceback.

    ## Return Format
    `{"success": False, "message": str, "error": str}`.

    ## Examples
    `_error_response("Could not reach learnbot-mcp", e)`
    """
    if exc is not None:
        log.exception("%s: %s", message, exc)
    else:
        log.error("%s", message)
    return {"success": False, "message": message, "error": str(exc) if exc else message}


@lifespan
async def _lifespan(_server):
    await init_db()
    log.info("classroom-mcp startup: DB ready")
    yield


mcp = FastMCP(
    name=cfg.server_name,
    version=__version__,
    instructions="Student and class management for fleet learning services",
    lifespan=_lifespan,
)


@mcp.tool(annotations=_READ_ONLY)
async def help() -> dict:
    """List all classroom-mcp tools with one-line descriptions.

    ## Return Format
    `{"success": True, "message": str, "tools": [{name, description}]}`.

    ## Examples
    `help()` — returns the full tool catalogue for this server.
    """
    try:
        tools = await mcp.list_tools()
        catalogue = [
            {"name": tool.name, "description": (tool.description or "").splitlines()[0]}
            for tool in sorted(tools, key=lambda t: t.name)
        ]
        return {
            "success": True,
            "message": f"{len(catalogue)} tools available.",
            "tools": catalogue,
            "count": len(catalogue),
        }
    except Exception as e:
        return _error_response("Could not list tools", e)


@mcp.tool(annotations=_READ_ONLY)
async def status() -> dict:
    """Report server health: version, ports, DB path, tool count.

    ## Return Format
    `{"success": True, "message": str, "server": str, "version": str, ...}`.

    ## Examples
    `status()` — liveness + inventory in one call.
    """
    try:
        tool_count: Any = len(await mcp.list_tools())
    except Exception:
        tool_count = "unknown"
    return {
        "success": True,
        "message": f"{cfg.server_name} v{__version__} healthy.",
        "server": cfg.server_name,
        "version": __version__,
        "backend_port": cfg.backend_port,
        "frontend_port": cfg.frontend_port,
        "db_path": cfg.db_path,
        "learnbot_url": cfg.learnbot_url,
        "tool_count": tool_count,
    }


@mcp.tool(annotations=_MUTATING)
async def server_shutdown(
    delay_seconds: Annotated[float, Field(description="Grace period before exit.")] = 0.5,
) -> dict:
    """Shut the MCP server down gracefully (lets agents stop the process).

    ## Return Format
    `{"success": True, "message": str}` — process exits after the delay.

    ## Examples
    `server_shutdown()` — orderly exit in 0.5 s.
    """

    async def _exit_later() -> None:
        await asyncio.sleep(max(0.0, delay_seconds))
        os._exit(0)

    asyncio.create_task(_exit_later())
    return {"success": True, "message": f"Shutting down in {delay_seconds} s."}


@mcp.tool(annotations=_MUTATING)
async def student_create(
    name: Annotated[str, Field(description="Student full name.")],
    email: Annotated[str, Field(description="Unique email; blank stores NULL.")] = "",
    language: Annotated[str, Field(description="Target language code, e.g. ja.")] = "ja",
    level: Annotated[str, Field(description="Proficiency level, e.g. N4.")] = "N4",
    framework: Annotated[
        str, Field(description="Framework: JLPT, CEFR, HSK, DELF, DELE, Goethe, etc.")
    ] = "JLPT",
    notes: Annotated[str, Field(description="Free-text notes.")] = "",
) -> dict:
    """Create or update a student by email.

    ## Return Format
    `{"success": bool, "student": {...}}` — created/updated row (or `error`).

    ## Examples
    `student_create(name="Aiko Tanaka", email="aiko@example.com", level="N4")`
    """
    return await _upsert_s(
        {
            "name": name,
            "email": email,
            "language": language,
            "level": level,
            "framework": framework,
            "notes": notes,
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def student_get(
    student_id: Annotated[int, Field(description="Student row ID.")],
) -> dict:
    """Get a student by ID.

    ## Return Format
    `{"success": bool, "student": {...}}` (or `error`).

    ## Examples
    `student_get(student_id=1)`
    """
    return await _get_s(student_id)


@mcp.tool(annotations=_READ_ONLY)
async def student_list(
    active_only: Annotated[bool, Field(description="Only active students.")] = True,
) -> dict:
    """List all students.

    ## Return Format
    `{"success": True, "message": str, "students": [...], "count": int}`.

    ## Examples
    `student_list()` — active students; `student_list(active_only=False)` — all.
    """
    students = await _list_s(active_only=active_only)
    return {
        "success": True,
        "message": f"{len(students)} student(s) found.",
        "students": students,
        "count": len(students),
    }


@mcp.tool(annotations=_MUTATING)
async def student_update(
    student_id: Annotated[int, Field(description="Student row ID.")],
    name: Annotated[str, Field(description="New name (blank keeps current).")] = "",
    email: Annotated[str, Field(description="New email (blank keeps current).")] = "",
    language: Annotated[str, Field(description="New language (blank keeps current).")] = "",
    level: Annotated[str, Field(description="New level (blank keeps current).")] = "",
    framework: Annotated[str, Field(description="JLPT, CEFR, HSK, DELF, DELE, Goethe, etc.")] = "",
    notes: Annotated[str, Field(description="New notes (blank keeps current).")] = "",
    active: Annotated[bool | None, Field(description="Set active flag.")] = None,
) -> dict:
    """Update a student's fields by ID.

    ## Return Format
    `{"success": bool, "student": {...}}` — merged row (or `error`).

    ## Examples
    `student_update(student_id=1, level="N3")`
    """
    data: dict = {}
    if name:
        data["name"] = name
    if email:
        data["email"] = email
    if language:
        data["language"] = language
    if level:
        data["level"] = level
    if framework:
        data["framework"] = framework
    if notes:
        data["notes"] = notes
    if active is not None:
        data["active"] = int(active)
    return await _update_s(student_id, data)


@mcp.tool(annotations=_MUTATING)
async def student_delete(
    student_id: Annotated[int, Field(description="Student row ID.")],
) -> dict:
    """Delete a student.

    ## Return Format
    `{"success": bool, "message": str}`.

    ## Examples
    `student_delete(student_id=1)`
    """
    ok = await _delete_s(student_id)
    return {
        "success": ok,
        "message": f"Student {student_id} deleted." if ok else f"Student {student_id} not found.",
    }


@mcp.tool(annotations=_MUTATING)
async def class_create(
    name: Annotated[str, Field(description="Class name.")],
    description: Annotated[str, Field(description="Class description.")] = "",
    language: Annotated[str, Field(description="Target language code, e.g. ja.")] = "ja",
    level: Annotated[str, Field(description="Proficiency level, e.g. N4.")] = "N4",
    framework: Annotated[
        str, Field(description="Framework: JLPT, CEFR, HSK, DELF, DELE, Goethe, etc.")
    ] = "JLPT",
    schedule: Annotated[str, Field(description="Schedule text, e.g. Mon/Wed 18:00.")] = "",
) -> dict:
    """Create a new class.

    ## Return Format
    `{"success": bool, "class": {...}}` — created row (or `error`).

    ## Examples
    `class_create(name="Japanese N4 Evening", schedule="Mon/Wed 18:00")`
    """
    return await _upsert_c(
        {
            "name": name,
            "description": description,
            "language": language,
            "level": level,
            "framework": framework,
            "schedule": schedule,
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def class_list() -> dict:
    """List all classes with student counts.

    ## Return Format
    `{"success": True, "message": str, "classes": [...], "count": int}`.

    ## Examples
    `class_list()`
    """
    classes = await _list_c()
    return {
        "success": True,
        "message": f"{len(classes)} class(es) found.",
        "classes": classes,
        "count": len(classes),
    }


@mcp.tool(annotations=_READ_ONLY)
async def class_get(
    class_id: Annotated[int, Field(description="Class row ID.")],
) -> dict:
    """Get a class by ID.

    ## Return Format
    `{"success": bool, "class": {...}}` (or `error`).

    ## Examples
    `class_get(class_id=1)`
    """
    return await _get_c(class_id)


@mcp.tool(annotations=_MUTATING)
async def class_add_student(
    class_id: Annotated[int, Field(description="Class row ID.")],
    student_id: Annotated[int, Field(description="Student row ID.")],
) -> dict:
    """Add a student to a class.

    ## Return Format
    `{"success": bool, ...}` with a human-readable `message`.

    ## Examples
    `class_add_student(class_id=1, student_id=2)`
    """
    result = await _add_s(class_id, student_id)
    result.setdefault(
        "message",
        f"Student {student_id} added to class {class_id}."
        if result.get("success")
        else "Could not add student to class.",
    )
    return result


@mcp.tool(annotations=_MUTATING)
async def class_remove_student(
    class_id: Annotated[int, Field(description="Class row ID.")],
    student_id: Annotated[int, Field(description="Student row ID.")],
) -> dict:
    """Remove a student from a class.

    ## Return Format
    `{"success": bool, ...}` with a human-readable `message`.

    ## Examples
    `class_remove_student(class_id=1, student_id=2)`
    """
    result = await _remove_s(class_id, student_id)
    result.setdefault(
        "message",
        f"Student {student_id} removed from class {class_id}."
        if result.get("success")
        else "Could not remove student from class.",
    )
    return result


@mcp.tool(annotations=_MUTATING)
async def class_update(
    class_id: Annotated[int, Field(description="Class row ID.")],
    name: Annotated[str, Field(description="New name (blank keeps current).")] = "",
    description: Annotated[str, Field(description="New description.")] = "",
    language: Annotated[str, Field(description="New language (blank keeps current).")] = "",
    level: Annotated[str, Field(description="New level (blank keeps current).")] = "",
    framework: Annotated[str, Field(description="JLPT, CEFR, HSK, DELF, DELE, Goethe, etc.")] = "",
    schedule: Annotated[str, Field(description="New schedule text.")] = "",
) -> dict:
    """Update a class's fields by ID.

    ## Return Format
    `{"success": bool, "class": {...}}` — merged row (or `error`).

    ## Examples
    `class_update(class_id=1, schedule="Tue/Thu 19:00")`
    """
    data: dict = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    if language:
        data["language"] = language
    if level:
        data["level"] = level
    if framework:
        data["framework"] = framework
    if schedule:
        data["schedule"] = schedule
    return await _update_c(class_id, data)


@mcp.tool(annotations=_MUTATING)
async def class_delete(
    class_id: Annotated[int, Field(description="Class row ID.")],
) -> dict:
    """Delete a class.

    ## Return Format
    `{"success": bool, "message": str}`.

    ## Examples
    `class_delete(class_id=1)`
    """
    ok = await _delete_c(class_id)
    return {
        "success": ok,
        "message": f"Class {class_id} deleted." if ok else f"Class {class_id} not found.",
    }


@mcp.tool(annotations=_MUTATING)
async def assignment_create(
    class_id: Annotated[int, Field(description="Owning class ID.")],
    title: Annotated[str, Field(description="Assignment title.")],
    description: Annotated[str, Field(description="Assignment description.")] = "",
    lesson_id: Annotated[int, Field(description="Linked learnbot lesson ID (0 = none).")] = 0,
    due_at: Annotated[str, Field(description="Due date text, e.g. 2026-10-15.")] = "",
    max_score: Annotated[float, Field(description="Maximum score.")] = 100,
) -> dict:
    """Create an assignment for a class.

    ## Return Format
    `{"success": bool, "assignment": {...}}` (or `error`).

    ## Examples
    `assignment_create(class_id=1, title="Kanji drill 1", due_at="2026-10-15")`
    """
    return await _create_a(
        {
            "class_id": class_id,
            "title": title,
            "description": description,
            "lesson_id": lesson_id,
            "due_at": due_at,
            "max_score": max_score,
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def assignment_list(
    class_id: Annotated[int, Field(description="Filter by class (0 = all).")] = 0,
) -> dict:
    """List assignments, optionally filtered by class.

    ## Return Format
    `{"success": True, "message": str, "assignments": [...], "count": int}`.

    ## Examples
    `assignment_list()` — all; `assignment_list(class_id=1)` — one class.
    """
    cid = class_id if class_id > 0 else None
    assignments = await _list_a(class_id=cid)
    return {
        "success": True,
        "message": f"{len(assignments)} assignment(s) found.",
        "assignments": assignments,
        "count": len(assignments),
    }


@mcp.tool(annotations=_MUTATING)
async def assignment_delete(
    assignment_id: Annotated[int, Field(description="Assignment row ID.")],
) -> dict:
    """Delete an assignment.

    ## Return Format
    `{"success": bool, "message": str}`.

    ## Examples
    `assignment_delete(assignment_id=3)`
    """
    ok = await _delete_a(assignment_id)
    return {
        "success": ok,
        "message": f"Assignment {assignment_id} deleted."
        if ok
        else f"Assignment {assignment_id} not found.",
    }


@mcp.tool(annotations=_MUTATING)
async def progress_record(
    student_id: Annotated[int, Field(description="Student row ID.")],
    assignment_id: Annotated[int, Field(description="Assignment ID (0 = none).")] = 0,
    lesson_id: Annotated[int, Field(description="Lesson ID (0 = none).")] = 0,
    score: Annotated[float, Field(description="Score achieved.")] = 0,
    time_spent: Annotated[int, Field(description="Minutes spent.")] = 0,
) -> dict:
    """Record progress for a student.

    ## Return Format
    `{"success": bool, "progress": {...}}` (or `error`).

    ## Examples
    `progress_record(student_id=1, assignment_id=2, score=85, time_spent=40)`
    """
    return await _upsert_p(
        {
            "student_id": student_id,
            "assignment_id": assignment_id,
            "lesson_id": lesson_id,
            "score": score,
            "time_spent": time_spent,
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def progress_list(
    student_id: Annotated[int, Field(description="Filter by student (0 = all).")] = 0,
    class_id: Annotated[int, Field(description="Filter by class (0 = all).")] = 0,
) -> dict:
    """List progress records, filtered by student or class.

    ## Return Format
    `{"success": True, "message": str, "records": [...], "count": int}`.

    ## Examples
    `progress_list(student_id=1)` — one student's history.
    """
    sid = student_id if student_id > 0 else None
    cid = class_id if class_id > 0 else None
    records = await _list_p(student_id=sid, class_id=cid)
    return {
        "success": True,
        "message": f"{len(records)} record(s) found.",
        "records": records,
        "count": len(records),
    }


# ── Course tools ──


@mcp.tool(annotations=_MUTATING)
async def course_create(
    code: Annotated[str, Field(description="Course code, e.g. ECON101.")],
    title: Annotated[str, Field(description="Course title.")],
    description: Annotated[str, Field(description="Course description.")] = "",
    subject: Annotated[str, Field(description="Subject area.")] = "",
    level: Annotated[str, Field(description="undergraduate/graduate/etc.")] = "undergraduate",
    credits: Annotated[int, Field(description="Credit points.")] = 3,
) -> dict:
    """Create a new course (ECON101, CS201, etc.).

    ## Return Format
    `{"success": bool, "course": {...}}` (or `error`).

    ## Examples
    `course_create(code="JP201", title="Intermediate Japanese", subject="Japanese")`
    """
    return await _upsert_course(
        {
            "code": code,
            "title": title,
            "description": description,
            "subject": subject,
            "level": level,
            "credits": credits,
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def course_list(
    subject: Annotated[str, Field(description="Filter by subject (blank = all).")] = "",
) -> dict:
    """List courses, optionally filtered by subject.

    ## Return Format
    `{"success": True, "message": str, "courses": [...], "count": int}`.

    ## Examples
    `course_list()` — all; `course_list(subject="Japanese")` — filtered.
    """
    courses = await _list_courses(subject=subject)
    return {
        "success": True,
        "message": f"{len(courses)} course(s) found.",
        "courses": courses,
        "count": len(courses),
    }


@mcp.tool(annotations=_READ_ONLY)
async def course_get(
    course_id: Annotated[int, Field(description="Course row ID.")],
) -> dict:
    """Get a course by ID.

    ## Return Format
    `{"success": bool, "course": {...}}` (or `error`).

    ## Examples
    `course_get(course_id=1)`
    """
    return await _get_course(course_id)


@mcp.tool(annotations=_MUTATING)
async def course_update(
    course_id: Annotated[int, Field(description="Course row ID.")],
    code: Annotated[str, Field(description="New code (blank keeps current).")] = "",
    title: Annotated[str, Field(description="New title (blank keeps current).")] = "",
    description: Annotated[str, Field(description="New description.")] = "",
    subject: Annotated[str, Field(description="New subject (blank keeps current).")] = "",
    level: Annotated[str, Field(description="New level (blank keeps current).")] = "",
    credits: Annotated[int, Field(description="New credits (0 keeps current).")] = 0,
) -> dict:
    """Update a course's fields by ID. Leave a field blank/0 to keep its current value.

    ## Return Format
    `{"success": bool, "course": {...}}` — merged row (or `error`).

    ## Examples
    `course_update(course_id=1, credits=4)`
    """
    data: dict = {}
    if code:
        data["code"] = code
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    if subject:
        data["subject"] = subject
    if level:
        data["level"] = level
    if credits:
        data["credits"] = credits
    return await _update_course(course_id, data)


@mcp.tool(annotations=_MUTATING)
async def course_delete(
    course_id: Annotated[int, Field(description="Course row ID.")],
) -> dict:
    """Delete a course.

    ## Return Format
    `{"success": bool, "message": str}`.

    ## Examples
    `course_delete(course_id=1)`
    """
    ok = await _del_course(course_id)
    return {
        "success": ok,
        "message": f"Course {course_id} deleted." if ok else f"Course {course_id} not found.",
    }


# ── Module tools ──


@mcp.tool(annotations=_MUTATING)
async def module_create(
    course_id: Annotated[int, Field(description="Owning course ID.")],
    title: Annotated[str, Field(description="Module title.")],
    sequence: Annotated[int, Field(description="Position in the course.")] = 1,
    description: Annotated[str, Field(description="Module description.")] = "",
    learning_objectives: Annotated[str, Field(description="JSON array of objective strings.")] = "",
) -> dict:
    """Create a module within a course. Objectives is a JSON array of strings.

    ## Return Format
    `{"success": bool, "module": {...}}` (or `error`).

    ## Examples
    `module_create(course_id=1, title="Hiragana basics", sequence=1)`
    """
    objs = json.loads(learning_objectives) if learning_objectives else []
    return await _create_mod(
        {
            "course_id": course_id,
            "title": title,
            "sequence": sequence,
            "description": description,
            "learning_objectives": json.dumps(objs),
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def module_list(
    course_id: Annotated[int, Field(description="Owning course ID.")],
) -> dict:
    """List modules for a course, ordered by sequence.

    ## Return Format
    `{"success": True, "message": str, "modules": [...], "count": int}`.

    ## Examples
    `module_list(course_id=1)`
    """
    modules = await _list_mods(course_id)
    return {
        "success": True,
        "message": f"{len(modules)} module(s) found.",
        "modules": modules,
        "count": len(modules),
    }


@mcp.tool(annotations=_MUTATING)
async def module_delete(
    module_id: Annotated[int, Field(description="Module row ID.")],
) -> dict:
    """Delete a module.

    ## Return Format
    `{"success": bool, "message": str}`.

    ## Examples
    `module_delete(module_id=2)`
    """
    ok = await _del_mod(module_id)
    return {
        "success": ok,
        "message": f"Module {module_id} deleted." if ok else f"Module {module_id} not found.",
    }


# ── Courseware tools ──


@mcp.tool(annotations=_MUTATING)
async def courseware_create(
    module_id: Annotated[int, Field(description="Owning module ID.")],
    title: Annotated[str, Field(description="Courseware title.")],
    type: Annotated[
        str, Field(description="lecture, reading, problem_set, quiz, project.")
    ] = "lecture",
    content: Annotated[str, Field(description="Markdown content.")] = "",
    source: Annotated[str, Field(description="ai_generated, human, imported.")] = "ai_generated",
    duration_min: Annotated[int, Field(description="Estimated minutes.")] = 0,
) -> dict:
    """Create courseware (lecture, reading, problem_set, quiz, project).

    ## Return Format
    `{"success": bool, "courseware": {...}}` (or `error`).

    ## Examples
    `courseware_create(module_id=1, title="Hiragana chart", type="reading")`
    """
    return await _create_cw(
        {
            "module_id": module_id,
            "title": title,
            "type": type,
            "content": content,
            "source": source,
            "duration_min": duration_min,
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def courseware_list(
    module_id: Annotated[int, Field(description="Owning module ID.")],
) -> dict:
    """List courseware items for a module.

    ## Return Format
    `{"success": True, "message": str, "courseware": [...], "count": int}`.

    ## Examples
    `courseware_list(module_id=1)`
    """
    items = await _list_cw(module_id)
    return {
        "success": True,
        "message": f"{len(items)} item(s) found.",
        "courseware": items,
        "count": len(items),
    }


@mcp.tool(annotations=_MUTATING)
async def courseware_delete(
    courseware_id: Annotated[int, Field(description="Courseware row ID.")],
) -> dict:
    """Delete a courseware item.

    ## Return Format
    `{"success": bool, "message": str}`.

    ## Examples
    `courseware_delete(courseware_id=5)`
    """
    ok = await _del_cw(courseware_id)
    return {
        "success": ok,
        "message": f"Courseware {courseware_id} deleted."
        if ok
        else f"Courseware {courseware_id} not found.",
    }


# ── Teaching Agent tools ──


@mcp.tool(annotations=_MUTATING)
async def agent_create(
    course_id: Annotated[int, Field(description="Owning course ID.")],
    name: Annotated[str, Field(description="Agent display name.")],
    role: Annotated[str, Field(description="lecturer, tutor, grader, designer.")] = "tutor",
    persona: Annotated[str, Field(description="Persona/system prompt text.")] = "",
    model: Annotated[str, Field(description="LLM model tag.")] = "llama3.2:3b",
) -> dict:
    """Create or update a teaching agent for a course. Role: lecturer, tutor, grader, designer.

    ## Return Format
    `{"success": bool, "agent": {...}}` (or `error`).

    ## Examples
    `agent_create(course_id=1, name="Sensei Bot", role="tutor")`
    """
    return await _upsert_agent(
        {"course_id": course_id, "name": name, "role": role, "persona": persona, "model": model}
    )


@mcp.tool(annotations=_READ_ONLY)
async def agent_list(
    course_id: Annotated[int, Field(description="Owning course ID.")],
) -> dict:
    """List teaching agents assigned to a course.

    ## Return Format
    `{"success": True, "message": str, "agents": [...], "count": int}`.

    ## Examples
    `agent_list(course_id=1)`
    """
    agents = await _list_agents(course_id)
    return {
        "success": True,
        "message": f"{len(agents)} agent(s) found.",
        "agents": agents,
        "count": len(agents),
    }


@mcp.tool(annotations=_MUTATING)
async def agent_delete(
    agent_id: Annotated[int, Field(description="Agent row ID.")],
) -> dict:
    """Remove a teaching agent.

    ## Return Format
    `{"success": bool, "message": str}`.

    ## Examples
    `agent_delete(agent_id=1)`
    """
    ok = await _del_agent(agent_id)
    return {
        "success": ok,
        "message": f"Agent {agent_id} deleted." if ok else f"Agent {agent_id} not found.",
    }


@mcp.tool(annotations=_MUTATING)
async def human_teacher_create(
    name: Annotated[str, Field(description="Teacher full name.")],
    email: Annotated[str, Field(description="Unique email; blank stores NULL.")] = "",
    bio: Annotated[str, Field(description="Short bio.")] = "",
    languages: Annotated[str, Field(description="Comma-separated, e.g. German,English.")] = "",
    specializations: Annotated[str, Field(description="Comma-separated, e.g. JLPT,Business.")] = "",
    rate_per_hour: Annotated[float, Field(description="Hourly rate.")] = 30,
    currency: Annotated[str, Field(description="ISO currency, e.g. EUR.")] = "EUR",
) -> dict:
    """Register a human teacher (freelance or school-affiliated).

    ## Return Format
    `{"success": bool, "teacher": {...}}` (or `error`).

    ## Examples
    `human_teacher_create(name="Maria S.", languages="German,English")`
    """
    lang_list = [lang.strip() for lang in languages.split(",") if lang.strip()] if languages else []
    spec_list = (
        [sk.strip() for sk in specializations.split(",") if sk.strip()] if specializations else []
    )
    return await _upsert_ht(
        {
            "name": name,
            "email": email,
            "bio": bio,
            "languages": json.dumps(lang_list),
            "specializations": json.dumps(spec_list),
            "rate_per_hour": rate_per_hour,
            "currency": currency,
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def human_teacher_list(
    available_only: Annotated[bool, Field(description="Only available teachers.")] = True,
) -> dict:
    """List registered human teachers, optionally only available ones.

    ## Return Format
    `{"success": True, "message": str, "teachers": [...], "count": int}`.

    ## Examples
    `human_teacher_list()` — available teachers.
    """
    teachers = await _list_ht(available_only=available_only)
    return {
        "success": True,
        "message": f"{len(teachers)} teacher(s) found.",
        "teachers": teachers,
        "count": len(teachers),
    }


@mcp.tool(annotations=_READ_ONLY)
async def human_teacher_get(
    teacher_id: Annotated[int, Field(description="Teacher row ID.")],
) -> dict:
    """Get a human teacher by ID.

    ## Return Format
    `{"success": bool, "teacher": {...}}` (or `error`).

    ## Examples
    `human_teacher_get(teacher_id=1)`
    """
    return await _get_ht(teacher_id)


@mcp.tool(annotations=_MUTATING)
async def human_teacher_delete(
    teacher_id: Annotated[int, Field(description="Teacher row ID.")],
) -> dict:
    """Remove a human teacher.

    ## Return Format
    `{"success": bool, "message": str}`.

    ## Examples
    `human_teacher_delete(teacher_id=1)`
    """
    ok = await _del_ht(teacher_id)
    return {
        "success": ok,
        "message": f"Teacher {teacher_id} deleted." if ok else f"Teacher {teacher_id} not found.",
    }


@mcp.tool(annotations=_MUTATING)
async def referral_create(
    student_id: Annotated[int, Field(description="Student row ID.")],
    teacher_id: Annotated[int, Field(description="Teacher row ID.")],
    reason: Annotated[str, Field(description="Why the referral was made.")] = "",
) -> dict:
    """Refer a student to a human teacher when the AI detects a need.

    ## Return Format
    `{"success": bool, "referral": {...}}` (or `error`).

    ## Examples
    `referral_create(student_id=1, teacher_id=2, reason="Needs speaking practice")`
    """
    return await _create_ref({"student_id": student_id, "teacher_id": teacher_id, "reason": reason})


@mcp.tool(annotations=_READ_ONLY)
async def referral_list(
    teacher_id: Annotated[int, Field(description="Filter by teacher (0 = all).")] = 0,
    status: Annotated[
        str, Field(description="Filter by status: pending/booked/completed (blank = all).")
    ] = "",
) -> dict:
    """List referrals, filtered by teacher or status (pending/booked/completed).

    ## Return Format
    `{"success": True, "message": str, "referrals": [...], "count": int}`.

    ## Examples
    `referral_list(status="pending")` — open referrals.
    """
    tid = teacher_id if teacher_id > 0 else None
    refs = await _list_refs(teacher_id=tid, status=status)
    return {
        "success": True,
        "message": f"{len(refs)} referral(s) found.",
        "referrals": refs,
        "count": len(refs),
    }


@mcp.tool(annotations=_MUTATING)
async def referral_update_status(
    referral_id: Annotated[int, Field(description="Referral row ID.")],
    status: Annotated[str, Field(description="pending, booked, completed, cancelled.")],
) -> dict:
    """Update referral status: pending → booked → completed → cancelled.

    ## Return Format
    `{"success": bool, ...}` with a human-readable `message`.

    ## Examples
    `referral_update_status(referral_id=1, status="booked")`
    """
    result = await _update_ref(referral_id, status)
    result.setdefault(
        "message",
        f"Referral {referral_id} set to {status}."
        if result.get("success")
        else "Could not update referral.",
    )
    return result


# ── AI Generation tools (framework-aware, uses learnbot-mcp LLM) ──


async def _llm_call(prompt: str, system_prompt: str = "", timeout: float = 60.0) -> str:
    """Call the LLM via learnbot-mcp's Ollama bridge or directly."""
    from classroom_mcp.config import get_settings as _cfg

    _c = _cfg()
    import httpx

    # Try learnbot-mcp LLM bridge first
    learnbot = _c.learnbot_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
            resp = await client.post(
                f"{learnbot}/api/llm/chat",
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "system_prompt": system_prompt,
                    "model": "",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", data.get("content", ""))
    except Exception:
        pass

    # Fallback to direct Ollama
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
            resp = await client.post(
                "http://127.0.0.1:11434/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "model": "llama3.2:3b",
                    "stream": False,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception:
        pass

    return ""


FRAMEWORK_DESCRIPTIONS = {
    "JLPT": "Japanese Language Proficiency Test - levels N5 (beginner) to N1 (advanced). Focus on kanji, vocabulary, grammar, reading, listening.",
    "CEFR": "Common European Framework of Reference for Languages - levels A1 (beginner) to C2 (mastery). Covers all four skills: reading, writing, speaking, listening. Used for European languages.",
    "HSK": "Hanyu Shuiping Kaoshi - Chinese proficiency test. Levels 1 (beginner) to 6 (advanced). Covers listening, reading, writing.",
    "DELF": "Diplome d'Etudes en Langue Francaise - French certification. Levels A1 to B2, covering all four skills.",
    "DALF": "Diplome Approfondi de Langue Francaise - Advanced French. Levels C1 to C2.",
    "DELE": "Diplomas de Espanol como Lengua Extranjera - Spanish certification. Levels A1 to C2.",
    "Goethe": "Goethe-Zertifikat - German certification. Levels A1 to C2.",
    "TOEFL": "Test of English as a Foreign Language - English proficiency for academic contexts.",
    "IELTS": "International English Language Testing System - English proficiency, band scores 1-9.",
}


def _framework_desc(framework: str) -> str:
    return FRAMEWORK_DESCRIPTIONS.get(
        framework.upper(), f"{framework} - standardised proficiency framework"
    )


@mcp.tool(annotations=_MUTATING)
async def syllabus_generate(
    course_id: Annotated[int, Field(description="Course to generate modules for.")],
    language: Annotated[str, Field(description="Target language code.")] = "ja",
    level: Annotated[str, Field(description="Proficiency level.")] = "N4",
    framework: Annotated[
        str, Field(description="JLPT, CEFR, HSK, DELF, DELE, Goethe, IELTS, TOEFL.")
    ] = "JLPT",
    num_modules: Annotated[int, Field(description="How many modules to create.")] = 8,
    ctx: Context | None = None,
) -> dict:
    """Generate a full syllabus for a course using AI, structured by framework level.

    Creates modules with learning objectives for the given course.
    Framework: JLPT, CEFR, HSK, DELF, DELE, Goethe, IELTS, TOEFL, etc.

    ## Return Format
    `{"success": True, "message": str, "course_id": int, "modules_created": int,
    "module_ids": [...]}` (or `success: False` with `error` when the LLM is
    unavailable or returns invalid JSON).

    ## Examples
    `syllabus_generate(course_id=1, level="N4", num_modules=8)`
    """
    if ctx is not None:
        await ctx.info(f"Generating {num_modules}-module syllabus for course {course_id}")
    from classroom_mcp.database import (
        course_get as _cg,
    )
    from classroom_mcp.database import (
        generated_content_save as _save,
    )
    from classroom_mcp.database import (
        module_create as _mc,
    )

    course = await _cg(course_id)
    if not course.get("success"):
        return course
    c = course["course"]
    framework_info = _framework_desc(framework)

    prompt = (
        f"Create a {num_modules}-module syllabus for a '{c['title']}' course "
        f"(language: {language}, level: {level}, framework: {framework_info}).\n\n"
        f"Course description: {c.get('description', '')}\n"
        f"Subject area: {c.get('subject', '')}\n\n"
        "Return a JSON array of modules, each with:\n"
        "- `title`: module title\n"
        "- `description`: 1-2 sentence summary\n"
        "- `learning_objectives`: array of 3-5 specific, measurable objectives\n"
        "- `duration_hours`: estimated hours to complete\n\n"
        "The modules should follow a logical pedagogical progression for this level. "
        "Reference the framework's known content requirements for each stage."
    )
    system_prompt = (
        f"You are an expert curriculum designer specialising in {framework} "
        f"({level}) language education. Design pedagogically sound syllabi."
    )

    raw = await _llm_call(prompt, system_prompt)
    if not raw:
        return _error_response("LLM unavailable - could not generate syllabus.", None) | {
            "error": "LLM unavailable - could not generate syllabus"
        }

    raw_clean = raw.replace("```json", "").replace("```", "").strip()
    start = raw_clean.find("[")
    end = raw_clean.rfind("]")
    if start != -1 and end != -1:
        raw_clean = raw_clean[start : end + 1]
    try:
        modules = json.loads(raw_clean)
    except json.JSONDecodeError as e:
        return _error_response("LLM returned invalid JSON", e) | {"raw": raw[:500]}

    created = []
    for i, mod in enumerate(modules[:num_modules]):
        obj = json.dumps(mod.get("learning_objectives", []))
        result = await _mc(
            {
                "course_id": course_id,
                "title": mod.get("title", f"Module {i + 1}"),
                "sequence": i + 1,
                "description": mod.get("description", ""),
                "learning_objectives": obj,
            }
        )
        if result.get("success"):
            created.append(result["module"]["id"])

    await _save(
        {
            "module_id": 0,
            "content_type": "syllabus",
            "framework": framework,
            "level": level,
            "prompt": prompt[:500],
            "content": raw,
        }
    )

    return {
        "success": True,
        "message": f"Syllabus generated: {len(created)} module(s) for course {course_id}.",
        "course_id": course_id,
        "modules_created": len(created),
        "module_ids": created,
        "framework": framework,
        "level": level,
    }


@mcp.tool(annotations=_MUTATING)
async def courseware_generate_ai(
    module_id: Annotated[int, Field(description="Module to generate content for.")],
    courseware_type: Annotated[
        str, Field(description="lecture, reading, problem_set, quiz, project.")
    ] = "lecture",
    duration_min: Annotated[int, Field(description="Target minutes.")] = 30,
    ctx: Context | None = None,
) -> dict:
    """Generate AI courseware content for a module at the right framework level.

    Courseware types: lecture, reading, problem_set, quiz, project.
    Uses the module's learning objectives and course framework to generate level-appropriate content.

    ## Return Format
    `{"success": True, "message": str, "module_id": int, "courseware_id": int}`
    (or `success: False` with `error` when the LLM is unavailable).

    ## Examples
    `courseware_generate_ai(module_id=1, courseware_type="quiz")`
    """
    if ctx is not None:
        await ctx.info(f"Generating {courseware_type} for module {module_id}")
    from classroom_mcp.database import (
        courseware_create as _ccw,
    )
    from classroom_mcp.database import (
        generated_content_save as _save,
    )
    from classroom_mcp.database import (
        module_list as _ml,
    )

    modules = await _ml(0)
    target = None
    for m in modules:
        if m["id"] == module_id:
            target = m
            break
    if not target:
        return {"success": False, "message": "Module not found.", "error": "Module not found"}

    objs = json.loads(target.get("learning_objectives", "[]"))
    objs_text = "\n".join(f"- {o}" for o in objs) if objs else "(not specified)"

    prompt = (
        f"Create a {courseware_type} (~{duration_min} min) for the module '{target['title']}'.\n\n"
        f"Description: {target.get('description', '')}\n"
        f"Learning objectives:\n{objs_text}\n\n"
        f"Return the content as structured markdown suitable for a language learner "
        f"at this level. Include clear explanations, examples, and practice prompts."
    )

    raw = await _llm_call(prompt)
    if not raw:
        return {"success": False, "message": "LLM unavailable.", "error": "LLM unavailable"}

    cw = await _ccw(
        {
            "module_id": module_id,
            "title": f"{courseware_type.title()}: {target['title']}",
            "type": courseware_type,
            "content": raw,
            "source": "ai_generated",
            "duration_min": duration_min,
        }
    )

    await _save(
        {
            "module_id": module_id,
            "content_type": courseware_type,
            "framework": "",
            "level": "",
            "prompt": prompt[:500],
            "content": raw,
        }
    )

    return {
        "success": True,
        "message": f"{courseware_type} generated for module {module_id}.",
        "module_id": module_id,
        "courseware_id": cw.get("courseware", {}).get("id"),
        "type": courseware_type,
    }


@mcp.tool(annotations=_MUTATING)
async def assignment_create_with_lesson(
    class_id: Annotated[int, Field(description="Owning class ID.")],
    title: Annotated[str, Field(description="Assignment title.")],
    description: Annotated[str, Field(description="Assignment description.")] = "",
    level: Annotated[str, Field(description="Level override (blank = class level).")] = "",
    language: Annotated[str, Field(description="Language override (blank = class language).")] = "",
    due_at: Annotated[str, Field(description="Due date text.")] = "",
    max_score: Annotated[float, Field(description="Maximum score.")] = 100,
    ctx: Context | None = None,
) -> dict:
    """Create an assignment and generate a corresponding lesson via learnbot-mcp.

    Calls learnbot-mcp's lesson_generate to produce lesson content, then
    creates the assignment linked to the generated lesson. This tool's
    contract is "assignment WITH lesson" - if lesson generation fails for
    any reason (learnbot unreachable, HTTP error, learnbot reports its own
    failure), this returns success: False and does NOT create the
    assignment. A bare assignment with no lesson is not what was asked
    for, so it is not reported as a success. Requires learnbot-mcp running
    and reachable at LEARNBOT_URL.

    ## Return Format
    `{"success": True, "message": str, "assignment": {...}, "generated_lesson": {...}}`
    (or `success: False` with `error` — and no assignment created).

    ## Examples
    `assignment_create_with_lesson(class_id=1, title="Greetings dialogue")`
    """
    if ctx is not None:
        await ctx.info(f"Creating assignment with lesson for class {class_id}")
    from classroom_mcp.database import assignment_create as _ac

    class_info = await class_get(class_id)
    if not class_info.get("success"):
        return class_info

    cls = class_info["class"]
    target_lang = language or cls.get("language", "ja")
    target_level = level or cls.get("level", "N4")
    target_framework = cls.get("framework", "JLPT")

    learnbot = cfg.learnbot_url.rstrip("/")
    import httpx

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            resp = await client.post(
                f"{learnbot}/api/lesson/generate",
                json={
                    "title": title,
                    "language": target_lang,
                    "level": target_level,
                    "framework": target_framework,
                    "duration_min": 30,
                },
            )
    except httpx.RequestError as e:
        return _error_response(f"Could not reach learnbot-mcp at {learnbot}", e)

    if resp.status_code != 200:
        return {
            "success": False,
            "message": f"learnbot-mcp lesson generation failed: HTTP {resp.status_code}.",
            "error": f"learnbot-mcp lesson generation failed: HTTP {resp.status_code} - {resp.text[:200]}",
        }

    lesson = resp.json()
    if not lesson.get("success"):
        return {
            "success": False,
            "message": "learnbot-mcp reported lesson generation failure.",
            "error": f"learnbot-mcp reported lesson generation failure: {lesson.get('error', 'unknown error')}",
        }

    result = await _ac(
        {
            "class_id": class_id,
            "title": title,
            "description": description,
            "lesson_id": lesson.get("lesson", {}).get("id", 0),
            "due_at": due_at,
            "max_score": max_score,
        }
    )
    if not result.get("success"):
        return result

    result["generated_lesson"] = lesson.get("lesson", {})
    result["message"] = f"Assignment '{title}' created with generated lesson."
    return result


@mcp.tool(annotations=_READ_ONLY)
async def syllabus_list(
    course_id: Annotated[int, Field(description="Filter by course (0 = all).")] = 0,
    content_type: Annotated[str, Field(description="Filter by type (blank = all).")] = "",
) -> dict:
    """List generated syllabus and courseware content.

    ## Return Format
    `{"success": True, "message": str, "content": [...], "count": int}`.

    ## Examples
    `syllabus_list(course_id=1)`
    """
    from classroom_mcp.database import generated_content_list as _gl

    items = await _gl(module_id=course_id, content_type=content_type)
    return {
        "success": True,
        "message": f"{len(items)} generated item(s) found.",
        "content": items,
        "count": len(items),
    }


@mcp.resource("classroom://status")
async def resource_status() -> str:
    """Live server status (version, ports, DB path) as JSON."""
    try:
        tool_count: Any = len(await mcp.list_tools())
    except Exception:
        tool_count = "unknown"
    return json.dumps(
        {
            "server": cfg.server_name,
            "version": __version__,
            "backend_port": cfg.backend_port,
            "db_path": cfg.db_path,
            "tool_count": tool_count,
        }
    )


@mcp.prompt()
async def plan_lesson(
    topic: Annotated[str, Field(description="Lesson topic.")],
    level: Annotated[str, Field(description="Proficiency level.")] = "N4",
    framework: Annotated[str, Field(description="JLPT, CEFR, HSK, DELF, DELE, Goethe.")] = "JLPT",
) -> str:
    """Build a lesson-planning prompt for a topic at a framework level.

    ## Return Format
    Rendered prompt text for the lesson request.

    ## Examples
    `plan_lesson(topic="ordering food", level="N5")`
    """
    return (
        f"Plan a language lesson about '{topic}' for a {framework} {level} learner. "
        f"Framework context: {_framework_desc(framework)}\n\n"
        "Include: 1) 3 concrete learning objectives, 2) key vocabulary (10 items "
        "with readings), 3) 2 grammar points with examples, 4) a short practice "
        "dialogue, 5) a 5-question check quiz. "
        "Use classroom-mcp tools to persist: courseware_create for the lesson text, "
        "then assignment_create to assign it to the class."
    )


def main():
    mcp.run(transport="stdio")
