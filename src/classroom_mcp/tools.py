"""MCP tools — student, class, assignment, progress management."""

from __future__ import annotations

import logging

from fastmcp.server.lifespan import lifespan
from fastmcp.server.server import FastMCP

from classroom_mcp._version import __version__
from classroom_mcp.config import get_settings
from classroom_mcp.database import (
    assignment_create as _create_a,
    assignment_delete as _delete_a,
    assignment_list as _list_a,
    class_add_student as _add_s,
    class_delete as _delete_c,
    class_get as _get_c,
    class_list as _list_c,
    class_remove_student as _remove_s,
    class_upsert as _upsert_c,
    init_db,
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


def main():
    mcp.run(transport="stdio")
