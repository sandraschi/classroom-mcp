"""Starlette REST API - student, class, assignment, progress endpoints."""

from __future__ import annotations

import logging
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from classroom_mcp._version import __version__
from classroom_mcp.config import get_settings
from classroom_mcp.database import (
    assignment_create,
    assignment_delete,
    assignment_list,
    class_add_student,
    class_delete,
    class_get,
    class_list,
    class_upsert,
    progress_list,
    progress_upsert,
    student_delete,
    student_get,
    student_list,
    student_upsert,
)

log = logging.getLogger(__name__)
cfg = get_settings()

_START_TIME = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)


async def api_health(request: Request) -> JSONResponse:
    uptime = (
        __import__("datetime").datetime.now(__import__("datetime").timezone.utc) - _START_TIME
    ).total_seconds()
    return JSONResponse(
        {
            "status": "ok",
            "server": cfg.server_name,
            "version": __version__,
            "uptime_seconds": int(uptime),
        }
    )


async def api_status(request: Request) -> JSONResponse:
    uptime = (
        __import__("datetime").datetime.now(__import__("datetime").timezone.utc) - _START_TIME
    ).total_seconds()
    try:
        from classroom_mcp.tools import mcp as _mcp

        tool_count = len(await _mcp.list_tools())
    except Exception:
        tool_count = -1
    return JSONResponse(
        {
            "status": "ok",
            "server": cfg.server_name,
            "version": __version__,
            "uptime_seconds": int(uptime),
            "backend_port": cfg.backend_port,
            "frontend_port": cfg.frontend_port,
            "db_path": cfg.db_path,
            "learnbot_url": cfg.learnbot_url,
            "tool_count": tool_count,
        }
    )


async def api_shutdown(request: Request) -> JSONResponse:
    import asyncio as _asyncio
    import os as _os

    async def _exit_later() -> None:
        await _asyncio.sleep(0.5)
        _os._exit(0)

    _asyncio.create_task(_exit_later())
    return JSONResponse({"success": True, "message": "Shutting down in 0.5 s."})


def _make_routes():
    """Build route list - avoids import-time eval of async functions."""

    async def api_student_list(request: Request) -> JSONResponse:
        active = request.query_params.get("active", "1") == "1"
        students = await student_list(active_only=active)
        return JSONResponse({"students": students, "count": len(students)})

    async def api_student_create(request: Request) -> JSONResponse:
        body = await request.json()
        result = await student_upsert(body)
        return JSONResponse(result)

    async def api_student_get(request: Request) -> JSONResponse:
        result = await student_get(int(request.path_params["id"]))
        status = 404 if not result.get("success") else 200
        return JSONResponse(result, status_code=status)

    async def api_student_delete(request: Request) -> JSONResponse:
        return JSONResponse({"success": await student_delete(int(request.path_params["id"]))})

    async def api_class_list(request: Request) -> JSONResponse:
        classes = await class_list()
        return JSONResponse({"classes": classes, "count": len(classes)})

    async def api_class_create(request: Request) -> JSONResponse:
        body = await request.json()
        result = await class_upsert(body)
        return JSONResponse(result)

    async def api_class_get(request: Request) -> JSONResponse:
        result = await class_get(int(request.path_params["id"]))
        status = 404 if not result.get("success") else 200
        return JSONResponse(result, status_code=status)

    async def api_class_delete(request: Request) -> JSONResponse:
        return JSONResponse({"success": await class_delete(int(request.path_params["id"]))})

    async def api_class_add_student(request: Request) -> JSONResponse:
        body = await request.json()
        result = await class_add_student(int(request.path_params["id"]), body["student_id"])
        return JSONResponse(result)

    async def api_assignments(request: Request) -> JSONResponse:
        cid = request.query_params.get("class_id")
        items = await assignment_list(class_id=int(cid) if cid else None)
        return JSONResponse({"assignments": items, "count": len(items)})

    async def api_assignment_create(request: Request) -> JSONResponse:
        body = await request.json()
        result = await assignment_create(body)
        return JSONResponse(result)

    async def api_assignment_delete(request: Request) -> JSONResponse:
        return JSONResponse({"success": await assignment_delete(int(request.path_params["id"]))})

    async def api_progress(request: Request) -> JSONResponse:
        sid = request.query_params.get("student_id")
        cid = request.query_params.get("class_id")
        records = await progress_list(
            student_id=int(sid) if sid else None, class_id=int(cid) if cid else None
        )
        return JSONResponse({"records": records, "count": len(records)})

    async def api_progress_record(request: Request) -> JSONResponse:
        body = await request.json()
        result = await progress_upsert(body)
        return JSONResponse(result)

    def _spa_fallback(request: Request) -> HTMLResponse:
        dist = Path(__file__).resolve().parents[2] / "web_sota" / "dist"
        index = dist / "index.html"
        if index.is_file():
            return HTMLResponse(index.read_text(encoding="utf-8"))
        return HTMLResponse("<h1>Frontend not built</h1>", status_code=503)

    routes: list = [
        Route("/health", api_health),
        Route("/api/health", api_health),
        Route("/api/students", api_student_list),
        Route("/api/students", api_student_create, methods=["POST"]),
        Route("/api/students/{id}", api_student_get),
        Route("/api/students/{id}", api_student_delete, methods=["DELETE"]),
        Route("/api/classes", api_class_list),
        Route("/api/classes", api_class_create, methods=["POST"]),
        Route("/api/classes/{id}", api_class_get),
        Route("/api/classes/{id}", api_class_delete, methods=["DELETE"]),
        Route("/api/classes/{id}/students", api_class_add_student, methods=["POST"]),
        Route("/api/assignments", api_assignments),
        Route("/api/assignments", api_assignment_create, methods=["POST"]),
        Route("/api/assignments/{id}", api_assignment_delete, methods=["DELETE"]),
        Route("/api/progress", api_progress),
        Route("/api/progress", api_progress_record, methods=["POST"]),
        Route("/api/status", api_status),
        Route("/api/shutdown", api_shutdown, methods=["POST"]),
    ]
    dist = Path(__file__).resolve().parents[2] / "web_sota" / "dist"
    if dist.is_dir() and (dist / "index.html").is_file():
        routes.append(Mount("/assets", StaticFiles(directory=str(dist / "assets")), name="assets"))
        routes.append(Route("/{path:path}", _spa_fallback))
    return routes


def build_app() -> Starlette:
    app = Starlette(routes=_make_routes())
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["tauri://localhost", "http://tauri.localhost", "https://tauri.localhost"],
        allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


def run_rest() -> None:
    import uvicorn

    app = build_app()
    log.info("classroom-mcp REST API on port %s", cfg.backend_port)
    uvicorn.run(app, host="0.0.0.0", port=cfg.backend_port, log_level="info")


if __name__ == "__main__":
    run_rest()
