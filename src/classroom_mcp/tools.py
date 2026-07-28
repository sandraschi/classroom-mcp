"""MCP tools — student, class, assignment, progress management."""

from __future__ import annotations

import logging

from fastmcp.server.lifespan import lifespan
from fastmcp.server.server import FastMCP

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
    name: str,
    email: str = "",
    language: str = "ja",
    level: str = "N4",
    framework: str = "JLPT",
    notes: str = "",
) -> dict:
    """Create or update a student by email. Framework: JLPT, CEFR, HSK, DELF, DELE, Goethe, etc."""
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
async def student_get(student_id: int) -> dict:
    """Get a student by ID."""
    return await _get_s(student_id)


@mcp.tool(annotations=_READ_ONLY)
async def student_list(active_only: bool = True) -> dict:
    """List all students."""
    students = await _list_s(active_only=active_only)
    return {"success": True, "students": students, "count": len(students)}


@mcp.tool(annotations=_MUTATING)
async def student_update(
    student_id: int,
    name: str = "",
    email: str = "",
    language: str = "",
    level: str = "",
    framework: str = "",
    notes: str = "",
    active: bool | None = None,
) -> dict:
    """Update a student's fields by ID. Framework: JLPT, CEFR, HSK, DELF, DELE, Goethe, etc."""
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
async def student_delete(student_id: int) -> dict:
    """Delete a student."""
    return {"success": await _delete_s(student_id)}


@mcp.tool(annotations=_MUTATING)
async def class_create(
    name: str,
    description: str = "",
    language: str = "ja",
    level: str = "N4",
    framework: str = "JLPT",
    schedule: str = "",
) -> dict:
    """Create a new class. Framework: JLPT, CEFR, HSK, DELF, DELE, Goethe, etc."""
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
async def class_update(
    class_id: int,
    name: str = "",
    description: str = "",
    language: str = "",
    level: str = "",
    framework: str = "",
    schedule: str = "",
) -> dict:
    """Update a class's fields by ID. Framework: JLPT, CEFR, HSK, DELF, DELE, Goethe, etc."""
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
async def course_update(
    course_id: int,
    code: str = "",
    title: str = "",
    description: str = "",
    subject: str = "",
    level: str = "",
    credits: int = 0,
) -> dict:
    """Update a course's fields by ID. Leave a field blank/0 to keep its current value."""
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
    "JLPT": "Japanese Language Proficiency Test — levels N5 (beginner) to N1 (advanced). Focus on kanji, vocabulary, grammar, reading, listening.",
    "CEFR": "Common European Framework of Reference for Languages — levels A1 (beginner) to C2 (mastery). Covers all four skills: reading, writing, speaking, listening. Used for European languages.",
    "HSK": "Hanyu Shuiping Kaoshi — Chinese proficiency test. Levels 1 (beginner) to 6 (advanced). Covers listening, reading, writing.",
    "DELF": "Diplome d'Etudes en Langue Francaise — French certification. Levels A1 to B2, covering all four skills.",
    "DALF": "Diplome Approfondi de Langue Francaise — Advanced French. Levels C1 to C2.",
    "DELE": "Diplomas de Espanol como Lengua Extranjera — Spanish certification. Levels A1 to C2.",
    "Goethe": "Goethe-Zertifikat — German certification. Levels A1 to C2.",
    "TOEFL": "Test of English as a Foreign Language — English proficiency for academic contexts.",
    "IELTS": "International English Language Testing System — English proficiency, band scores 1-9.",
}


def _framework_desc(framework: str) -> str:
    return FRAMEWORK_DESCRIPTIONS.get(
        framework.upper(), f"{framework} — standardised proficiency framework"
    )


@mcp.tool(annotations=_MUTATING)
async def syllabus_generate(
    course_id: int,
    language: str = "ja",
    level: str = "N4",
    framework: str = "JLPT",
    num_modules: int = 8,
) -> dict:
    """Generate a full syllabus for a course using AI, structured by framework level.

    Creates modules with learning objectives for the given course.
    Framework: JLPT, CEFR, HSK, DELF, DELE, Goethe, IELTS, TOEFL, etc.
    """
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
        return {"success": False, "error": "LLM unavailable — could not generate syllabus"}

    import json

    raw_clean = raw.replace("```json", "").replace("```", "").strip()
    start = raw_clean.find("[")
    end = raw_clean.rfind("]")
    if start != -1 and end != -1:
        raw_clean = raw_clean[start : end + 1]
    try:
        modules = json.loads(raw_clean)
    except json.JSONDecodeError:
        return {"success": False, "error": "LLM returned invalid JSON", "raw": raw[:500]}

    created = []
    for i, mod in enumerate(modules[:num_modules]):
        import json as _j

        obj = _j.dumps(mod.get("learning_objectives", []))
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
        "course_id": course_id,
        "modules_created": len(created),
        "module_ids": created,
        "framework": framework,
        "level": level,
    }


@mcp.tool(annotations=_MUTATING)
async def courseware_generate_ai(
    module_id: int,
    courseware_type: str = "lecture",
    duration_min: int = 30,
) -> dict:
    """Generate AI courseware content for a module at the right framework level.

    Courseware types: lecture, reading, problem_set, quiz, project.
    Uses the module's learning objectives and course framework to generate level-appropriate content.
    """
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
        return {"success": False, "error": "Module not found"}

    import json as _j

    objs = _j.loads(target.get("learning_objectives", "[]"))
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
        return {"success": False, "error": "LLM unavailable"}

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
        "module_id": module_id,
        "courseware_id": cw.get("courseware", {}).get("id"),
        "type": courseware_type,
    }


@mcp.tool(annotations=_MUTATING)
async def assignment_create_with_lesson(
    class_id: int,
    title: str,
    description: str = "",
    level: str = "",
    language: str = "",
    due_at: str = "",
    max_score: float = 100,
) -> dict:
    """Create an assignment and generate a corresponding lesson via learnbot-mcp.

    Calls learnbot-mcp's lesson_generate to produce lesson content, then
    creates the assignment linked to the generated lesson. This tool's
    contract is "assignment WITH lesson" — if lesson generation fails for
    any reason (learnbot unreachable, HTTP error, learnbot reports its own
    failure), this returns success: False and does NOT create the
    assignment. A bare assignment with no lesson is not what was asked
    for, so it is not reported as a success. Requires learnbot-mcp running
    and reachable at LEARNBOT_URL.
    """
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
        return {
            "success": False,
            "error": f"Could not reach learnbot-mcp at {learnbot}: {e}",
        }

    if resp.status_code != 200:
        return {
            "success": False,
            "error": f"learnbot-mcp lesson generation failed: HTTP {resp.status_code} - {resp.text[:200]}",
        }

    lesson = resp.json()
    if not lesson.get("success"):
        return {
            "success": False,
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
    return result


@mcp.tool(annotations=_READ_ONLY)
async def syllabus_list(course_id: int = 0, content_type: str = "") -> dict:
    """List generated syllabus and courseware content."""
    from classroom_mcp.database import generated_content_list as _gl

    items = await _gl(module_id=course_id, content_type=content_type)
    return {"success": True, "content": items, "count": len(items)}


def main():
    mcp.run(transport="stdio")
