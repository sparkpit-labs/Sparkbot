import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

OWNER = {"X-Sparkbot-Local": "1"}


@pytest.fixture()
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("SPARKBOT_ROUNDTABLE_JOBS_PER_HOUR", raising=False)
    return tmp_path


@pytest.fixture()
def client(data_dir: Path) -> TestClient:
    return TestClient(app, base_url="http://127.0.0.1:8000")


def make_room(client: TestClient, name: str = "Planning") -> dict:
    response = client.post("/roundtable/rooms", json={"name": name}, headers=OWNER)
    assert response.status_code == 201
    return response.json()


def make_seat(client: TestClient, room_id: str, slug: str, name: str | None = None) -> dict:
    response = client.post(
        f"/roundtable/rooms/{room_id}/seats", json={"display_name": name or slug.title(), "slug": slug}, headers=OWNER
    )
    assert response.status_code == 201, response.text
    return response.json()


def seat_headers(seat: dict) -> dict:
    return {"Authorization": f"Bearer {seat['key']}"}


def say(client: TestClient, room_id: str, content: str) -> dict:
    response = client.post(f"/roundtable/rooms/{room_id}/messages", json={"content": content}, headers=OWNER)
    assert response.status_code == 201, response.text
    return response.json()


def messages(client: TestClient, room_id: str) -> list[dict]:
    return client.get(f"/roundtable/rooms/{room_id}/messages", headers=OWNER).json()["messages"]


def claim(client: TestClient, seat: dict) -> dict | None:
    response = client.get("/roundtable/seat/jobs/next", headers=seat_headers(seat))
    if response.status_code == 204:
        return None
    assert response.status_code == 200, response.text
    return response.json()["job"]


def test_owner_routes_need_the_local_header_and_a_loopback_host(data_dir: Path) -> None:
    local = TestClient(app, base_url="http://127.0.0.1:8000")
    assert local.get("/roundtable/rooms").status_code == 403
    assert local.get("/roundtable/rooms", headers=OWNER).status_code == 200
    rebound = TestClient(app, base_url="http://attacker.example")
    assert rebound.get("/roundtable/rooms", headers=OWNER).status_code == 403


def test_cors_allows_the_frontend_origin_only(client: TestClient) -> None:
    preflight = {"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "x-sparkbot-local,content-type"}
    ok = client.options("/roundtable/rooms", headers={"Origin": "http://127.0.0.1:5173", **preflight})
    assert ok.status_code == 200
    assert ok.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    bad = client.options("/roundtable/rooms", headers={"Origin": "https://evil.example", **preflight})
    assert "access-control-allow-origin" not in bad.headers


def test_rooms_and_seats(client: TestClient, data_dir: Path) -> None:
    room = make_room(client)
    assert room["paused"] is False
    seat = make_seat(client, room["id"], "claude", "Claude")
    assert seat["key"].startswith(f"rts_{seat['id']}_")

    detail = client.get(f"/roundtable/rooms/{room['id']}", headers=OWNER).json()
    assert [s["slug"] for s in detail["seats"]] == ["claude"]
    assert "key" not in detail["seats"][0] and "key_hash" not in detail["seats"][0]
    assert detail["seats"][0]["presence"] == "offline"

    # The key is only stored as a hash.
    raw = sqlite3.connect(data_dir / "sparkbot_public.sqlite3").execute("SELECT key_hash FROM roundtable_seats").fetchone()[0]
    assert seat["key"].split("_", 2)[2] not in raw

    dup = client.post(f"/roundtable/rooms/{room['id']}/seats", json={"display_name": "Again", "slug": "claude"}, headers=OWNER)
    assert dup.status_code == 409
    reserved = client.post(f"/roundtable/rooms/{room['id']}/seats", json={"display_name": "All", "slug": "all"}, headers=OWNER)
    assert reserved.status_code == 400

    me = client.get("/roundtable/seat/me", headers=seat_headers(seat)).json()
    assert me["seat"]["slug"] == "claude"
    assert me["rooms"] == [{"id": room["id"], "name": "Planning", "role": "agent"}]
    assert client.get(f"/roundtable/rooms/{room['id']}/seats", headers=OWNER).json()["seats"][0]["presence"] == "online"


def test_seat_keys_are_checked_and_can_be_rotated_or_removed(client: TestClient) -> None:
    room = make_room(client)
    seat = make_seat(client, room["id"], "codex")
    assert client.get("/roundtable/seat/me").status_code == 401
    assert client.get("/roundtable/seat/me", headers={"Authorization": "Bearer rts_nope_nope"}).status_code == 401
    # A seat key is not an owner credential.
    assert client.get("/roundtable/rooms", headers=seat_headers(seat)).status_code == 403

    rotated = client.post(f"/roundtable/rooms/{room['id']}/seats/{seat['id']}/rotate", headers=OWNER).json()
    assert client.get("/roundtable/seat/me", headers=seat_headers(seat)).status_code == 401
    assert client.get("/roundtable/seat/me", headers=seat_headers(rotated)).status_code == 200

    assert client.delete(f"/roundtable/rooms/{room['id']}/seats/{seat['id']}", headers=OWNER).status_code == 204
    assert client.get("/roundtable/seat/me", headers=seat_headers(rotated)).status_code == 401


def test_seat_only_sees_its_own_room(client: TestClient) -> None:
    mine = make_room(client, "Mine")
    other = make_room(client, "Other")
    seat = make_seat(client, mine["id"], "codex")
    say(client, other["id"], "secret plans")
    say(client, mine["id"], "hello room")
    seen = client.get("/roundtable/seat/messages", headers=seat_headers(seat)).json()["messages"]
    assert [m["content"] for m in seen] == ["hello room"]


def test_mention_creates_one_job_and_complete_posts_one_reply(client: TestClient) -> None:
    room = make_room(client)
    codex = make_seat(client, room["id"], "codex", "Codex")
    claude = make_seat(client, room["id"], "claude", "Claude")

    trigger = say(client, room["id"], "@codex @codex status of the build?")
    assert claim(client, claude) is None
    job = claim(client, codex)
    assert job is not None and claim(client, codex) is None
    assert job["trigger"]["id"] == trigger["id"]
    assert job["trigger"]["sender_type"] == "HUMAN"
    assert job["context"][-1]["content"] == "@codex @codex status of the build?"
    assert job["attempt"] == 1

    working = client.get(f"/roundtable/rooms/{room['id']}/seats", headers=OWNER).json()["seats"][0]
    assert working["presence"] == "working"

    beat = client.post(f"/roundtable/seat/jobs/{job['id']}/heartbeat", json={"claim_token": job["claim_token"], "note": "thinking"}, headers=seat_headers(codex))
    assert beat.status_code == 200
    assert client.get(f"/roundtable/rooms/{room['id']}/seats", headers=OWNER).json()["seats"][0]["working_note"] == "thinking"

    body = {"claim_token": job["claim_token"], "content": "Build is green."}
    first = client.post(f"/roundtable/seat/jobs/{job['id']}/complete", json=body, headers=seat_headers(codex))
    again = client.post(f"/roundtable/seat/jobs/{job['id']}/complete", json=body, headers=seat_headers(codex))
    assert first.status_code == again.status_code == 200
    assert first.json()["message"]["id"] == again.json()["message"]["id"]
    replies = [m for m in messages(client, room["id"]) if m["reply_to_id"] == trigger["id"]]
    assert [(m["sender_name"], m["sender_kind"]) for m in replies] == [("Codex", "agent")]

    stale = client.post(f"/roundtable/seat/jobs/{job['id']}/complete", json={"claim_token": "wrong", "content": "x"}, headers=seat_headers(codex))
    assert stale.status_code == 409 and stale.json()["status"] == "done"
    # Another seat can't touch this job.
    assert client.post(f"/roundtable/seat/jobs/{job['id']}/heartbeat", json={"claim_token": job["claim_token"]}, headers=seat_headers(claude)).status_code == 404


def test_at_all_wakes_every_agent_and_agents_never_wake_agents(client: TestClient) -> None:
    room = make_room(client)
    codex = make_seat(client, room["id"], "codex")
    claude = make_seat(client, room["id"], "claude")
    say(client, room["id"], "@all one word each")
    assert claim(client, codex) is not None
    assert claim(client, claude) is not None

    posted = client.post("/roundtable/seat/messages", json={"content": "@claude over to you"}, headers=seat_headers(codex))
    assert posted.status_code == 201
    assert claim(client, claude) is None

    bad_reply = client.post("/roundtable/seat/messages", json={"content": "hi", "reply_to_id": "missing"}, headers=seat_headers(codex))
    assert bad_reply.status_code == 400


def test_pause_cancels_open_jobs_and_resume_restarts(client: TestClient) -> None:
    room = make_room(client)
    codex = make_seat(client, room["id"], "codex")
    say(client, room["id"], "@codex first")
    job = claim(client, codex)
    say(client, room["id"], "@codex second")

    say(client, room["id"], "/pause")
    assert client.get(f"/roundtable/rooms/{room['id']}", headers=OWNER).json()["paused"] is True
    late = client.post(f"/roundtable/seat/jobs/{job['id']}/complete", json={"claim_token": job["claim_token"], "content": "late"}, headers=seat_headers(codex))
    assert late.status_code == 409 and late.json()["status"] == "cancelled"
    assert claim(client, codex) is None

    say(client, room["id"], "@codex while paused")
    assert claim(client, codex) is None
    assert "paused" in messages(client, room["id"])[-1]["content"]

    say(client, room["id"], "/resume")
    say(client, room["id"], "@codex after resume")
    resumed = claim(client, codex)
    assert resumed is not None and resumed["trigger"]["content"] == "@codex after resume"
    assert all("late" != m["content"] for m in messages(client, room["id"]))

    paused = client.post(f"/roundtable/rooms/{room['id']}/pause", json={"paused": True}, headers=OWNER)
    assert paused.json()["paused"] is True


def test_hourly_cap_skips_with_a_notice(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPARKBOT_ROUNDTABLE_JOBS_PER_HOUR", "1")
    room = make_room(client)
    codex = make_seat(client, room["id"], "codex")
    say(client, room["id"], "@codex one")
    say(client, room["id"], "@codex two")
    assert "limit of 1 answers per hour" in messages(client, room["id"])[-1]["content"]
    assert claim(client, codex) is not None
    assert claim(client, codex) is None


def test_fail_with_retry_requeues_once_then_reports(client: TestClient) -> None:
    room = make_room(client)
    codex = make_seat(client, room["id"], "codex", "Codex")
    say(client, room["id"], "@codex try")
    job = claim(client, codex)
    first = client.post(f"/roundtable/seat/jobs/{job['id']}/fail", json={"claim_token": job["claim_token"], "error": "busy", "retry": True}, headers=seat_headers(codex))
    assert first.json()["job"]["status"] == "pending"
    job = claim(client, codex)
    assert job["attempt"] == 2
    second = client.post(f"/roundtable/seat/jobs/{job['id']}/fail", json={"claim_token": job["claim_token"], "error": "busy", "retry": True}, headers=seat_headers(codex))
    assert second.json()["job"]["status"] == "failed"
    assert messages(client, room["id"])[-1]["content"] == "Codex could not answer (busy)."


def test_expired_lease_goes_back_to_pending_once(client: TestClient, data_dir: Path) -> None:
    room = make_room(client)
    codex = make_seat(client, room["id"], "codex")
    say(client, room["id"], "@codex slow one")

    def expire() -> None:
        with sqlite3.connect(data_dir / "sparkbot_public.sqlite3") as db:
            db.execute("UPDATE roundtable_jobs SET lease_expires_at = '2000-01-01T00:00:00Z'")

    first = claim(client, codex)
    expire()
    second = claim(client, codex)
    assert second is not None and second["id"] == first["id"] and second["attempt"] == 2
    old = client.post(f"/roundtable/seat/jobs/{first['id']}/heartbeat", json={"claim_token": first["claim_token"]}, headers=seat_headers(codex))
    assert old.status_code == 409
    expire()
    assert claim(client, codex) is None


def test_messages_after_cursor_and_room_delete(client: TestClient) -> None:
    room = make_room(client)
    first = say(client, room["id"], "one")
    say(client, room["id"], "two")
    newer = client.get(f"/roundtable/rooms/{room['id']}/messages", params={"after": first["seq"]}, headers=OWNER).json()["messages"]
    assert [m["content"] for m in newer] == ["two"]
    make_seat(client, room["id"], "codex")
    assert client.delete(f"/roundtable/rooms/{room['id']}", headers=OWNER).status_code == 204
    assert client.get(f"/roundtable/rooms/{room['id']}", headers=OWNER).status_code == 404
    assert client.get("/roundtable/rooms", headers=OWNER).json() == {"rooms": []}
