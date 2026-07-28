"""Test student_upsert email collision handling."""

from __future__ import annotations

import pytest


class TestStudentUpsert:
    """student_upsert must handle email collisions — upsert by email, not crash."""

    @pytest.mark.asyncio
    async def test_create_then_update_by_email(self, db):
        from classroom_mcp.database import student_get, student_upsert

        r1 = await student_upsert(
            {
                "name": "Ali",
                "email": "ali@test.at",
                "language": "ar",
                "level": "A1",
                "framework": "CEFR",
            }
        )
        assert r1["success"] is True
        sid = r1["student"]["id"]

        got = await student_get(sid)
        assert got["success"] is True
        assert got["student"]["name"] == "Ali"
        assert got["student"]["email"] == "ali@test.at"
        assert got["student"]["framework"] == "CEFR"

    @pytest.mark.asyncio
    async def test_upsert_same_email_updates_not_duplicates(self, db):
        from classroom_mcp.database import student_list, student_upsert

        r1 = await student_upsert(
            {"name": "Ali", "email": "ali@test.at", "language": "ar", "level": "A1"}
        )
        assert r1["success"] is True

        r2 = await student_upsert(
            {"name": "Ali New", "email": "ali@test.at", "language": "de", "level": "A2"}
        )
        assert r2["success"] is True
        assert r2["student"]["id"] == r1["student"]["id"]

        all_s = await student_list(active_only=False)
        matches = [s for s in all_s if s["email"] == "ali@test.at"]
        assert len(matches) == 1, f"Expected 1 student, got {len(matches)}"
        assert matches[0]["name"] == "Ali New"

    @pytest.mark.asyncio
    async def test_upsert_without_email_creates_separate(self, db):
        from classroom_mcp.database import student_upsert

        r1 = await student_upsert({"name": "No Email", "language": "de"})
        assert r1["success"] is True

        r2 = await student_upsert({"name": "No Email 2", "language": "de"})
        assert r2["success"] is True
        assert r2["student"]["id"] != r1["student"]["id"]

    @pytest.mark.asyncio
    async def test_student_update_preserves_framework(self, db):
        from classroom_mcp.database import student_get, student_update, student_upsert

        r = await student_upsert(
            {
                "name": "Test",
                "email": "t@t.at",
                "language": "ar",
                "level": "A1",
                "framework": "CEFR",
            }
        )
        sid = r["student"]["id"]

        await student_update(sid, {"name": "Test Updated"})
        got = await student_get(sid)
        assert got["student"]["name"] == "Test Updated"
        assert got["student"]["framework"] == "CEFR"
        assert got["student"]["level"] == "A1"
