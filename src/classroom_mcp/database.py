"""Database layer — aiosqlite, schema, CRUD helpers."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

import aiosqlite

from classroom_mcp.config import get_settings

log = logging.getLogger(__name__)

_db_initialized = False
_init_lock = asyncio.Lock()
_db_conn: aiosqlite.Connection | None = None
_db_pool_lock = asyncio.Lock()


def clear_db_init_guard() -> None:
    global _db_initialized
    _db_initialized = False


async def close_db_pool() -> None:
    global _db_conn
    async with _db_pool_lock:
        if _db_conn is not None:
            await _db_conn.close()
            _db_conn = None


@asynccontextmanager
async def get_db():
    yield await _get_pooled_connection()


async def _get_pooled_connection() -> aiosqlite.Connection:
    global _db_conn
    cfg = get_settings()
    import os

    os.makedirs(os.path.dirname(cfg.db_path) or ".", exist_ok=True)
    async with _db_pool_lock:
        if _db_conn is None:
            pending = aiosqlite.connect(cfg.db_path)
            pending.daemon = True
            _db_conn = await pending
            _db_conn.row_factory = aiosqlite.Row
            await _db_conn.execute("PRAGMA journal_mode=WAL")
            await _db_conn.execute("PRAGMA foreign_keys=ON")
        return _db_conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE,
    token       TEXT DEFAULT '',
    language    TEXT DEFAULT 'ja',
    level       TEXT DEFAULT 'N4',
    notes       TEXT DEFAULT '',
    active      INTEGER DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS classes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    language    TEXT DEFAULT 'ja',
    level       TEXT DEFAULT 'N4',
    schedule    TEXT DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS class_students (
    class_id    INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    student_id  INTEGER REFERENCES students(id) ON DELETE CASCADE,
    PRIMARY KEY (class_id, student_id)
);

CREATE TABLE IF NOT EXISTS assignments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id    INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    description TEXT DEFAULT '',
    lesson_id   INTEGER DEFAULT 0,
    due_at      TEXT,
    assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
    max_score   REAL DEFAULT 100
);

CREATE TABLE IF NOT EXISTS progress (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      INTEGER REFERENCES students(id) ON DELETE CASCADE,
    assignment_id   INTEGER REFERENCES assignments(id) ON DELETE CASCADE,
    lesson_id       INTEGER DEFAULT 0,
    score           REAL,
    time_spent      INTEGER DEFAULT 0,
    vocab_mastered  INTEGER DEFAULT 0,
    vocab_total     INTEGER DEFAULT 0,
    completed_at    TEXT,
    UNIQUE(student_id, assignment_id)
);
"""


async def init_db() -> None:
    global _db_initialized
    async with _init_lock:
        if _db_initialized:
            return
        async with get_db() as db:
            await db.executescript(SCHEMA)
            await db.commit()
        _db_initialized = True


# ── Students ──


async def student_upsert(data: dict[str, Any]) -> dict:
    async with get_db() as db:
        try:
            cur = await db.execute(
                "INSERT INTO students (name, email, token, language, level, notes) VALUES (?,?,?,?,?,?)",
                (
                    data["name"],
                    data.get("email", ""),
                    data.get("token", ""),
                    data.get("language", "ja"),
                    data.get("level", "N4"),
                    data.get("notes", ""),
                ),
            )
            await db.commit()
            sid = cur.lastrowid
        except aiosqlite.IntegrityError:
            await db.execute(
                "UPDATE students SET name=?, language=?, level=?, notes=?, updated_at=datetime('now') WHERE email=?",
                (
                    data["name"],
                    data.get("language", "ja"),
                    data.get("level", "N4"),
                    data.get("notes", ""),
                    data.get("email", ""),
                ),
            )
            await db.commit()
            cur = await db.execute("SELECT id FROM students WHERE email=?", (data["email"],))
            row = await cur.fetchone()
            sid = row["id"] if row else None
    return (
        await student_get(sid) if sid else {"success": False, "error": "Could not create student"}
    )


async def student_get(student_id: int) -> dict:
    async with get_db() as db:
        cur = await db.execute("SELECT * FROM students WHERE id=?", (student_id,))
        row = await cur.fetchone()
        if not row:
            return {"success": False, "error": "Student not found"}
        return {"success": True, "student": dict(row)}


async def student_list(active_only: bool = True, class_id: int | None = None) -> list[dict]:
    async with get_db() as db:
        if class_id:
            cur = await db.execute(
                """SELECT s.* FROM students s JOIN class_students cs ON cs.student_id=s.id
                   WHERE cs.class_id=? AND (?=0 OR s.active=1) ORDER BY s.name""",
                (class_id, int(active_only)),
            )
        else:
            cur = await db.execute(
                "SELECT * FROM students WHERE (?=0 OR active=1) ORDER BY name",
                (int(active_only),),
            )
        return [dict(r) for r in await cur.fetchall()]


async def student_delete(student_id: int) -> bool:
    async with get_db() as db:
        cur = await db.execute("DELETE FROM students WHERE id=?", (student_id,))
        await db.commit()
        return cur.rowcount > 0


# ── Classes ──


async def class_upsert(data: dict[str, Any]) -> dict:
    async with get_db() as db:
        try:
            cur = await db.execute(
                "INSERT INTO classes (name, description, language, level, schedule) VALUES (?,?,?,?,?)",
                (
                    data["name"],
                    data.get("description", ""),
                    data.get("language", "ja"),
                    data.get("level", "N4"),
                    data.get("schedule", ""),
                ),
            )
            await db.commit()
            return {"success": True, "class": {"id": cur.lastrowid, "name": data["name"]}}
        except Exception as e:
            return {"success": False, "error": str(e)}


async def class_list() -> list[dict]:
    async with get_db() as db:
        cur = await db.execute(
            "SELECT c.*, (SELECT COUNT(*) FROM class_students WHERE class_id=c.id) as student_count FROM classes c ORDER BY c.name"
        )
        return [dict(r) for r in await cur.fetchall()]


async def class_get(class_id: int) -> dict:
    async with get_db() as db:
        cur = await db.execute("SELECT * FROM classes WHERE id=?", (class_id,))
        row = await cur.fetchone()
        if not row:
            return {"success": False, "error": "Class not found"}
        return {"success": True, "class": dict(row)}


async def class_add_student(class_id: int, student_id: int) -> dict:
    async with get_db() as db:
        try:
            await db.execute(
                "INSERT OR IGNORE INTO class_students (class_id, student_id) VALUES (?,?)",
                (class_id, student_id),
            )
            await db.commit()
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": True}


async def class_remove_student(class_id: int, student_id: int) -> dict:
    async with get_db() as db:
        cur = await db.execute(
            "DELETE FROM class_students WHERE class_id=? AND student_id=?", (class_id, student_id)
        )
        await db.commit()
    return {"success": cur.rowcount > 0}


async def class_delete(class_id: int) -> bool:
    async with get_db() as db:
        cur = await db.execute("DELETE FROM classes WHERE id=?", (class_id,))
        await db.commit()
        return cur.rowcount > 0


# ── Assignments ──


async def assignment_create(data: dict[str, Any]) -> dict:
    async with get_db() as db:
        cur = await db.execute(
            "INSERT INTO assignments (class_id, title, description, lesson_id, due_at, max_score) VALUES (?,?,?,?,?,?)",
            (
                data["class_id"],
                data["title"],
                data.get("description", ""),
                data.get("lesson_id", 0),
                data.get("due_at"),
                data.get("max_score", 100),
            ),
        )
        await db.commit()
        return {"success": True, "assignment": {"id": cur.lastrowid}}


async def assignment_list(class_id: int | None = None) -> list[dict]:
    async with get_db() as db:
        if class_id:
            cur = await db.execute(
                "SELECT * FROM assignments WHERE class_id=? ORDER BY due_at ASC", (class_id,)
            )
        else:
            cur = await db.execute(
                "SELECT a.*, c.name as class_name FROM assignments a JOIN classes c ON c.id=a.class_id ORDER BY a.due_at ASC"
            )
        return [dict(r) for r in await cur.fetchall()]


async def assignment_delete(assignment_id: int) -> bool:
    async with get_db() as db:
        cur = await db.execute("DELETE FROM assignments WHERE id=?", (assignment_id,))
        await db.commit()
        return cur.rowcount > 0


# ── Progress ──


async def progress_upsert(data: dict[str, Any]) -> dict:
    async with get_db() as db:
        try:
            await db.execute(
                """INSERT INTO progress (student_id, assignment_id, lesson_id, score, time_spent, vocab_mastered, vocab_total, completed_at)
                   VALUES (?,?,?,?,?,?,?,datetime('now'))""",
                (
                    data["student_id"],
                    data.get("assignment_id", 0),
                    data.get("lesson_id", 0),
                    data.get("score"),
                    data.get("time_spent", 0),
                    data.get("vocab_mastered", 0),
                    data.get("vocab_total", 0),
                ),
            )
        except aiosqlite.IntegrityError:
            await db.execute(
                "UPDATE progress SET score=?, time_spent=?, vocab_mastered=?, vocab_total=?, completed_at=datetime('now') WHERE student_id=? AND assignment_id=?",
                (
                    data.get("score"),
                    data.get("time_spent", 0),
                    data.get("vocab_mastered", 0),
                    data.get("vocab_total", 0),
                    data["student_id"],
                    data.get("assignment_id", 0),
                ),
            )
        await db.commit()
    return {"success": True}


async def progress_list(student_id: int | None = None, class_id: int | None = None) -> list[dict]:
    async with get_db() as db:
        if student_id:
            cur = await db.execute(
                "SELECT p.*, a.title as assignment_title FROM progress p LEFT JOIN assignments a ON a.id=p.assignment_id WHERE p.student_id=? ORDER BY p.completed_at DESC",
                (student_id,),
            )
        elif class_id:
            cur = await db.execute(
                """SELECT p.*, s.name as student_name, a.title as assignment_title FROM progress p
                JOIN students s ON s.id=p.student_id JOIN assignments a ON a.id=p.assignment_id
                JOIN class_students cs ON cs.student_id=s.id WHERE cs.class_id=? ORDER BY p.completed_at DESC""",
                (class_id,),
            )
        else:
            cur = await db.execute(
                "SELECT p.*, s.name as student_name, a.title as assignment_title FROM progress p LEFT JOIN students s ON s.id=p.student_id LEFT JOIN assignments a ON a.id=p.assignment_id ORDER BY p.completed_at DESC LIMIT 50"
            )
        return [dict(r) for r in await cur.fetchall()]
