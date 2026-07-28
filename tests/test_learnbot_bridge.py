"""Test the learnbot-mcp bridge — assignment_create_with_lesson.

Contract: this tool's whole point is "assignment WITH lesson." If lesson
generation fails for any reason, it must NOT create a bare assignment and
report success anyway — see CHANGELOG 0.2.0 for why (it silently did
exactly that until this fix).
"""
from __future__ import annotations

import pytest


class TestLearnbotBridge:
    """assignment_create_with_lesson must fail honestly when learnbot is down."""

    @pytest.mark.asyncio
    async def test_fails_cleanly_when_learnbot_unreachable(self, db, monkeypatch):
        from classroom_mcp.database import class_upsert, student_upsert, class_add_student
        from classroom_mcp.tools import assignment_create_with_lesson
        from classroom_mcp.config import clear_settings_cache

        monkeypatch.setenv("LEARNBOT_URL", "http://127.0.0.1:11999")
        clear_settings_cache()

        cls = await class_upsert({"name": "Test Class"})
        cid = cls["class"]["id"]

        stu = await student_upsert({"name": "Test Student", "email": "s@t.at"})
        sid = stu["student"]["id"]
        await class_add_student(cid, sid)

        result = await assignment_create_with_lesson(
            class_id=cid,
            title="German A1 Test",
            description="Test assignment",
            level="A1",
            language="de",
        )
        assert result["success"] is False, (
            "Bridge must report failure when learnbot is unreachable, "
            "not silently create a bare assignment."
        )
        assert "error" in result

        from classroom_mcp.database import assignment_list

        assignments = await assignment_list(class_id=cid)
        assert len(assignments) == 0, (
            "No assignment should exist when lesson generation failed — "
            "this tool's contract is assignment WITH lesson, not either/or."
        )

    @pytest.mark.asyncio
    async def test_url_path_matches_learnbot_route(self):
        """The bridge must call the route learnbot-mcp actually exposes.

        learnbot-mcp's api.py registers POST /api/lesson/generate (singular).
        This test reads the real source instead of hardcoding a string, so
        a future rename on either side fails this test instead of silently
        404ing in production like it did before this fix.
        """
        import inspect
        from classroom_mcp import tools

        src = inspect.getsource(tools.assignment_create_with_lesson)
        assert "/api/lesson/generate" in src, (
            "assignment_create_with_lesson must POST to /api/lesson/generate "
            "(singular) — that's the route learnbot-mcp's api.py registers."
        )
        assert "/api/lessons/generate" not in src, (
            "Found the plural /api/lessons/generate — that route doesn't "
            "exist in learnbot-mcp and will 404."
        )
