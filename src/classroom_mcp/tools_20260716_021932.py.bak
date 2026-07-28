"""MCP tools — student, class, assignment, progress management."""

from __future__ import annotations

import logging

from fastmcp.server.lifespan import lifespan
from fastmcp.server.server import FastMCP

from classroom_mcp._version import __version__
from classroom_mcp.config import get_settings
from classroom_mcp.database import (
    agent_delete as _del_agent,
    agent_list as _list_agents,
    agent_upsert as _upsert_agent,
    human_teacher_delete as _del_ht,
    human_teacher_get as _get_ht,
    human_teacher_list as _list_ht,
    human_teacher_upsert as _upsert_ht,
    referral_create as _create_ref,
    referral_list as _list_refs,
    referral_update_status as _update_ref,
    assignment_create as _create_a,
    assignment_delete as _delete_a,
    assignment_list as _list_a,
    class_add_student as _add_s,
    class_delete as _delete_c,
    class_get as _get_c,
    class_list as _list_c,
    class_remove_student as _remove_s,
    class_upsert as _upsert_c,
    course_delete as _del_course,
    course_get as _get_course,
    course_list as _list_courses,
    course_upsert as _upsert_course,
    courseware_create as _create_cw,
    courseware_delete as _del_cw,
    courseware_list as _list_cw,
    init_db,
    module_create as _create_mod,
    module_delete as _del_mod,
    module_list as _list_mods,
    progress_list as _list_p,
    progress_upsert as _upsert_p,
    student_delete as _delete_s,
    student_get as _get_s,
    student_list as _list_s,
    student_upsert as _upsert_s,
)

log = logging.getLogger(__name__)
cfg = get_settings()

_READ_ONLY = {"readonly": True}
_MUTATING: dict = {}


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


@mcp.tool(annotations=_MUTATING)
async def student_create(
    name: str, email: str = "", language: str = "ja", level: str = "N4", notes: str = ""
) -> dict:
    """Create or update a student by email."""
    return await _upsert_s(
        {"name": name, "email": email, "language": language, "level": level, "notes": notes}
    )


@mcp.tool(annotations=_READ_ONLY)
async def student_get(student_id: int) -> dict:
    """Get a student by ID."""
    return await _get_s(student_id)


@mcp.tool(annotations=_READ_ONLY)
async def student_list(active_only: bool = True) -> dict:
    """List all students."""
    students = await _list_s(active_only=active_only)
    return {"success": True, "students": students, "count": len(students)}


@mcp.tool(annotations=_MUTATING)
async def student_delete(student_id: int) -> dict:
    """Delete a student."""
    return {"success": await _delete_s(student_id)}


@mcp.tool(annotations=_MUTATING)
async def class_create(
    name: str, description: str = "", language: str = "ja", level: str = "N4", schedule: str = ""
) -> dict:
    """Create a new class."""
    return await _upsert_c(
        {
            "name": name,
            "description": description,
            "language": language,
            "level": level,
            "schedule": schedule,
        }
    )


@mcp.tool(annotations=_READ_ONLY)
async def class_list() -> dict:
    """List all classes with student counts."""
    classes = await _list_c()
    return {"success": True, "classes": classes, "count": len(classes)}


@mcp.tool(annotations=_READ_ONLY)
async def class_get(class_id: int) -> dict:
    """Get a class by ID."""
    return await _get_c(class_id)


@mcp.tool(annotations=_MUTATING)
async def class_add_student(class_id: int, student_id: int) -> dict:
    """Add a student to a class."""
    return await _add_s(class_id, student_id)


@mcp.tool(annotations=_MUTATING)
async def class_remove_student(class_id: int, student_id: int) -> dict:
    """Remove a student from a class."""
    return await _remove_s(class_id, student_id)


@mcp.tool(annotations=_MUTATING)
async def class_delete(class_id: int) -> dict:
    """Delete a class."""
    return {"success": await _delete_c(class_id)}


@mcp.tool(annotations=_MUTATING)
async def assignment_create(
    class_id: int,
    title: str,
    description: str = "",
    lesson_id: int = 0,
    due_at: str = "",
    max_score: float = 100,
) -> dict:
    """Create an assignment for a class."""
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
async def assignment_list(class_id: int = 0) -> dict:
    """List assignments, optionally filtered by class."""
    cid = class_id if class_id > 0 else None
    assignments = await _list_a(class_id=cid)
    return {"success": True, "assignments": assignments, "count": len(assignments)}


@mcp.tool(annotations=_MUTATING)
async def assignment_delete(assignment_id: int) -> dict:
    """Delete an assignment."""
    return {"success": await _delete_a(assignment_id)}


@mcp.tool(annotations=_MUTATING)
async def progress_record(
    student_id: int,
    assignment_id: int = 0,
    lesson_id: int = 0,
    score: float = 0,
    time_spent: int = 0,
) -> dict:
    """Record progress for a student."""
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
async def progress_list(student_id: int = 0, class_id: int = 0) -> dict:
    """List progress records, filtered by student or class."""
    sid = student_id if student_id > 0 else None
    cid = class_id if class_id > 0 else None
    records = await _list_p(student_id=sid, class_id=cid)
    return {"success": True, "records": records, "count": len(records)}


# ── Course tools ──


@mcp.tool(annotations=_MUTATING)
async def course_create(
    code: str,
    title: str,
    description: str = "",
    subject: str = "",
    level: str = "undergraduate",
    credits: int = 3,
) -> dict:
    """Create a new course (ECON101, CS201, etc.)."""
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
async def course_list(subject: str = "") -> dict:
    """List courses, optionally filtered by subject."""
    courses = await _list_courses(subject=subject)
    return {"success": True, "courses": courses, "count": len(courses)}


@mcp.tool(annotations=_READ_ONLY)
async def course_get(course_id: int) -> dict:
    """Get a course by ID."""
    return await _get_course(course_id)


@mcp.tool(annotations=_MUTATING)
async def course_delete(course_id: int) -> dict:
    """Delete a course."""
    return {"success": await _del_course(course_id)}


# ── Module tools ──


@mcp.tool(annotations=_MUTATING)
async def module_create(
    course_id: int,
    title: str,
    sequence: int = 1,
    description: str = "",
    learning_objectives: str = "",
) -> dict:
    """Create a module within a course. Objectives is a JSON array of strings."""
    import json

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
async def module_list(course_id: int) -> dict:
    """List modules for a course, ordered by sequence."""
    modules = await _list_mods(course_id)
    return {"success": True, "modules": modules, "count": len(modules)}


@mcp.tool(annotations=_MUTATING)
async def module_delete(module_id: int) -> dict:
    """Delete a module."""
    return {"success": await _del_mod(module_id)}


# ── Courseware tools ──


@mcp.tool(annotations=_MUTATING)
async def courseware_create(
    module_id: int,
    title: str,
    type: str = "lecture",
    content: str = "",
    source: str = "ai_generated",
    duration_min: int = 0,
) -> dict:
    """Create courseware (lecture, reading, problem_set, quiz, project)."""
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
async def courseware_list(module_id: int) -> dict:
    """List courseware items for a module."""
    items = await _list_cw(module_id)
    return {"success": True, "courseware": items, "count": len(items)}


@mcp.tool(annotations=_MUTATING)
async def courseware_delete(courseware_id: int) -> dict:
    """Delete a courseware item."""
    return {"success": await _del_cw(courseware_id)}


# ── Teaching Agent tools ──


@mcp.tool(annotations=_MUTATING)
async def agent_create(
    course_id: int, name: str, role: str = "tutor", persona: str = "", model: str = "llama3.2:3b"
) -> dict:
    """Create or update a teaching agent for a course. Role: lecturer, tutor, grader, designer."""
    return await _upsert_agent(
        {"course_id": course_id, "name": name, "role": role, "persona": persona, "model": model}
    )


@mcp.tool(annotations=_READ_ONLY)
async def agent_list(course_id: int) -> dict:
    """List teaching agents assigned to a course."""
    agents = await _list_agents(course_id)
    return {"success": True, "agents": agents, "count": len(agents)}


@mcp.tool(annotations=_MUTATING)
async def agent_delete(agent_id: int) -> dict:
    """Remove a teaching agent."""
    return {"success": await _del_agent(agent_id)}


@mcp.tool(annotations=_MUTATING)
async def human_teacher_create(
    name: str,
    email: str = "",
    bio: str = "",
    languages: str = "",
    specializations: str = "",
    rate_per_hour: float = 30,
    currency: str = "EUR",
) -> dict:
    """Register a human teacher (freelance or school-affiliated)."""
    import json

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
async def human_teacher_list(available_only: bool = True) -> dict:
    """List registered human teachers, optionally only available ones."""
    teachers = await _list_ht(available_only=available_only)
    return {"success": True, "teachers": teachers, "count": len(teachers)}


@mcp.tool(annotations=_READ_ONLY)
async def human_teacher_get(teacher_id: int) -> dict:
    """Get a human teacher by ID."""
    return await _get_ht(teacher_id)


@mcp.tool(annotations=_MUTATING)
async def human_teacher_delete(teacher_id: int) -> dict:
    """Remove a human teacher."""
    return {"success": await _del_ht(teacher_id)}


@mcp.tool(annotations=_MUTATING)
async def referral_create(student_id: int, teacher_id: int, reason: str = "") -> dict:
    """Refer a student to a human teacher when the AI detects a need."""
    return await _create_ref({"student_id": student_id, "teacher_id": teacher_id, "reason": reason})


@mcp.tool(annotations=_READ_ONLY)
async def referral_list(teacher_id: int = 0, status: str = "") -> dict:
    """List referrals, filtered by teacher or status (pending/booked/completed)."""
    tid = teacher_id if teacher_id > 0 else None
    refs = await _list_refs(teacher_id=tid, status=status)
    return {"success": True, "referrals": refs, "count": len(refs)}


@mcp.tool(annotations=_MUTATING)
async def referral_update_status(referral_id: int, status: str) -> dict:
    """Update referral status: pending → booked → completed → cancelled."""
    return await _update_ref(referral_id, status)


def main():
    mcp.run(transport="stdio")
