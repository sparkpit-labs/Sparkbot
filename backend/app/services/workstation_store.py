from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator


DATA_DIR_ENV = "SPARKBOT_DATA_DIR"
DEFAULT_SEATS = [
    ("meetings_manager", "openrouter", "openrouter/openai/gpt-4o-mini"),
    ("researcher", "openrouter", "openrouter/openai/gpt-4o-mini"),
    ("analyst", "openrouter", "openrouter/openai/gpt-4o-mini"),
    ("writer", "openrouter", "openrouter/openai/gpt-4o-mini"),
    ("builder", "openrouter", "openrouter/openai/gpt-4o-mini"),
    ("researcher", "default", ""),
    ("analyst", "default", ""),
    ("writer", "default", ""),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def data_dir() -> Path:
    configured = os.getenv(DATA_DIR_ENV)
    base = Path(configured) if configured else Path("data") / "command-center"
    base.mkdir(parents=True, exist_ok=True)
    return base


def database_path() -> Path:
    return data_dir() / "workstation.sqlite3"


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


SENSITIVE_KEY_PARTS = ("api_key", "access_key", "credential", "password", "secret", "token")
CONFIRMATION_TTL_SECONDS = 15 * 60


def _parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if any(part in key_text.lower() for part in SENSITIVE_KEY_PARTS):
                safe[key_text] = "[redacted]"
            else:
                safe[key_text] = _sanitize_payload(item)
        return safe
    if isinstance(value, list):
        return [_sanitize_payload(item) for item in value]
    return value


class WorkstationStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or database_path()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            self.ensure_schema(conn)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS seats (
              seat_index INTEGER PRIMARY KEY,
              label TEXT NOT NULL,
              agent TEXT NOT NULL,
              provider TEXT NOT NULL,
              model TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS rooms (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              status TEXT NOT NULL,
              phase TEXT NOT NULL,
              goal TEXT NOT NULL,
              summary TEXT NOT NULL,
              metadata_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS room_participants (
              id TEXT PRIMARY KEY,
              room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
              seat_index INTEGER,
              agent TEXT NOT NULL,
              provider TEXT NOT NULL,
              model TEXT NOT NULL,
              role TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chat_sessions (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              status TEXT NOT NULL,
              active_room_id TEXT NOT NULL,
              metadata_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chat_messages (
              id TEXT PRIMARY KEY,
              session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              actor TEXT NOT NULL,
              provider TEXT NOT NULL,
              model TEXT NOT NULL,
              metadata_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notes (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              body TEXT NOT NULL,
              surface TEXT NOT NULL,
              source_id TEXT NOT NULL,
              actor TEXT NOT NULL,
              tags_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS memory_entries (
              id TEXT PRIMARY KEY,
              content TEXT NOT NULL,
              memory_type TEXT NOT NULL,
              source_surface TEXT NOT NULL,
              source_id TEXT NOT NULL,
              actor TEXT NOT NULL,
              tags_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
              id TEXT PRIMARY KEY,
              event_type TEXT NOT NULL,
              surface TEXT NOT NULL,
              source_id TEXT NOT NULL,
              actor TEXT NOT NULL,
              summary TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS action_confirmations (
              id TEXT PRIMARY KEY,
              action_type TEXT NOT NULL,
              status TEXT NOT NULL,
              risk_level TEXT NOT NULL,
              prompt TEXT NOT NULL,
              surface TEXT NOT NULL,
              source_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              expires_at TEXT NOT NULL DEFAULT '',
              resolved_at TEXT,
              used_at TEXT
            );
            """
        )
        self._ensure_confirmation_columns(conn)
        self._seed_seats(conn)

    def _ensure_confirmation_columns(self, conn: sqlite3.Connection) -> None:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(action_confirmations)").fetchall()}
        if "expires_at" not in columns:
            conn.execute("ALTER TABLE action_confirmations ADD COLUMN expires_at TEXT NOT NULL DEFAULT ''")
        if "used_at" not in columns:
            conn.execute("ALTER TABLE action_confirmations ADD COLUMN used_at TEXT")

    def _seed_seats(self, conn: sqlite3.Connection) -> None:
        existing = conn.execute("SELECT COUNT(*) AS count FROM seats").fetchone()["count"]
        if existing:
            return
        now = utc_now()
        conn.executemany(
            """
            INSERT INTO seats (seat_index, label, agent, provider, model, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (idx + 1, f"Seat {idx + 1}", agent, provider, model, now)
                for idx, (agent, provider, model) in enumerate(DEFAULT_SEATS)
            ],
        )

    def list_seats(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM seats ORDER BY seat_index").fetchall()
        return [self._seat(row) for row in rows]

    def update_seat(self, seat_index: int, payload: dict[str, str], actor: str = "operator") -> dict[str, Any]:
        if seat_index < 1 or seat_index > 32:
            raise ValueError("Seat index must be between 1 and 32.")
        current = self.get_seat(seat_index)
        now = utc_now()
        label = payload.get("label") or current.get("label") or f"Seat {seat_index}"
        agent = payload.get("agent") or current.get("agent") or "meetings_manager"
        provider = payload.get("provider") or current.get("provider") or "default"
        model = payload.get("model") if payload.get("model") is not None else current.get("model", "")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO seats (seat_index, label, agent, provider, model, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(seat_index) DO UPDATE SET
                  label = excluded.label,
                  agent = excluded.agent,
                  provider = excluded.provider,
                  model = excluded.model,
                  updated_at = excluded.updated_at
                """,
                (seat_index, label, agent, provider, model or "", now),
            )
            row = conn.execute("SELECT * FROM seats WHERE seat_index = ?", (seat_index,)).fetchone()
            self._append_event_conn(
                conn,
                "seat.updated",
                "seats",
                str(seat_index),
                actor,
                f"Seat {seat_index} updated.",
                {"seat_index": seat_index, "agent": agent, "provider": provider, "model": model or ""},
                now,
            )
        return self._seat(row)

    def get_seat(self, seat_index: int) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM seats WHERE seat_index = ?", (seat_index,)).fetchone()
        if row:
            return self._seat(row)
        idx = seat_index - 1
        agent, provider, model = DEFAULT_SEATS[idx % len(DEFAULT_SEATS)]
        return {"seat_index": seat_index, "label": f"Seat {seat_index}", "agent": agent, "provider": provider, "model": model}

    def list_rooms(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM rooms ORDER BY updated_at DESC LIMIT ?", (max(1, min(limit, 200)),)).fetchall()
        return [self._room(row) for row in rows]

    def create_room(self, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        room_id = str(uuid.uuid4())
        now = utc_now()
        title = str(payload.get("title") or payload.get("name") or "Workstation Room").strip()
        status = str(payload.get("status") or "open").strip()
        phase = str(payload.get("phase") or "setup").strip()
        goal = str(payload.get("goal") or "").strip()
        summary = str(payload.get("summary") or "").strip()
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO rooms (id, title, status, phase, goal, summary, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (room_id, title, status, phase, goal, summary, _json_dumps(metadata), now, now),
            )
            seats = self._list_seats_conn(conn)
            for seat in seats:
                conn.execute(
                    """
                    INSERT INTO room_participants (id, room_id, seat_index, agent, provider, model, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        room_id,
                        seat["seat_index"],
                        seat["agent"],
                        seat["provider"],
                        seat["model"],
                        "seat",
                        now,
                    ),
                )
            self._append_event_conn(
                conn,
                "room.created",
                "rooms",
                room_id,
                actor,
                f"Room created: {title}",
                {"room_id": room_id, "title": title, "phase": phase},
                now,
            )
            row = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
            participants = self._list_room_participants_conn(conn, room_id)
        room = self._room(row)
        room["participants"] = participants
        return room

    def get_room(self, room_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
            if not row:
                return None
            participants = self._list_room_participants_conn(conn, room_id)
            notes = self._list_notes_conn(conn, surface="room", source_id=room_id, limit=50)
        room = self._room(row)
        room["participants"] = participants
        room["notes"] = notes
        return room

    def update_room(self, room_id: str, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any] | None:
        current = self.get_room(room_id)
        if not current:
            return None
        now = utc_now()
        next_room = {
            "title": str(payload.get("title", current["title"])).strip(),
            "status": str(payload.get("status", current["status"])).strip(),
            "phase": str(payload.get("phase", current["phase"])).strip(),
            "goal": str(payload.get("goal", current["goal"])).strip(),
            "summary": str(payload.get("summary", current["summary"])).strip(),
            "metadata": payload.get("metadata") if isinstance(payload.get("metadata"), dict) else current["metadata"],
        }
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE rooms SET title = ?, status = ?, phase = ?, goal = ?, summary = ?, metadata_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    next_room["title"],
                    next_room["status"],
                    next_room["phase"],
                    next_room["goal"],
                    next_room["summary"],
                    _json_dumps(next_room["metadata"]),
                    now,
                    room_id,
                ),
            )
            self._append_event_conn(
                conn,
                "room.updated",
                "rooms",
                room_id,
                actor,
                f"Room updated: {next_room['title']}",
                {"room_id": room_id, "phase": next_room["phase"], "status": next_room["status"]},
                now,
            )
        return self.get_room(room_id)

    def list_chat_sessions(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM chat_sessions ORDER BY updated_at DESC LIMIT ?",
                (max(1, min(limit, 200)),),
            ).fetchall()
            sessions = [self._chat_session(row) for row in rows]
            for session in sessions:
                session["last_message"] = self._last_chat_message_conn(conn, session["id"])
                session["message_count"] = int(
                    conn.execute("SELECT COUNT(*) AS count FROM chat_messages WHERE session_id = ?", (session["id"],)).fetchone()["count"]
                )
        return sessions

    def create_chat_session(self, payload: dict[str, Any] | None = None, actor: str = "operator") -> dict[str, Any]:
        payload = payload or {}
        session_id = str(uuid.uuid4())
        now = utc_now()
        title = str(payload.get("title") or "Sparkbot chat").strip()[:160] or "Sparkbot chat"
        active_room_id = str(payload.get("active_room_id") or "").strip()
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_sessions (id, title, status, active_room_id, metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, title, str(payload.get("status") or "open"), active_room_id, _json_dumps(_sanitize_payload(metadata)), now, now),
            )
            self._append_event_conn(
                conn,
                "chat.session.created",
                "chat",
                session_id,
                actor,
                f"Chat session created: {title}",
                {"session_id": session_id, "title": title},
                now,
            )
            row = conn.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
        session = self._chat_session(row)
        session["messages"] = []
        session["notes"] = []
        return session

    def get_chat_session(self, session_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                return None
            messages = self._list_chat_messages_conn(conn, session_id)
            notes = self._list_notes_conn(conn, surface="chat", source_id=session_id, limit=50)
        session = self._chat_session(row)
        session["messages"] = messages
        session["notes"] = notes
        session["message_count"] = len(messages)
        session["last_message"] = messages[-1] if messages else None
        return session

    def add_chat_message(self, session_id: str, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any] | None:
        role = str(payload.get("role") or "user").strip().lower()
        if role not in {"user", "assistant", "system"}:
            raise ValueError("Unsupported chat message role.")
        content = str(payload.get("content") or "").strip()
        if not content:
            raise ValueError("Chat message content is required.")
        message_id = str(uuid.uuid4())
        now = utc_now()
        provider = str(payload.get("provider") or "local").strip()
        model = str(payload.get("model") or "local-workstation").strip()
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        with self.connect() as conn:
            session = conn.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
            if not session:
                return None
            conn.execute(
                """
                INSERT INTO chat_messages (id, session_id, role, content, actor, provider, model, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (message_id, session_id, role, content, actor, provider, model, _json_dumps(_sanitize_payload(metadata)), now),
            )
            if role == "user" and session["title"] == "Sparkbot chat":
                title = content[:80] + ("..." if len(content) > 80 else "")
                conn.execute("UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?", (title, now, session_id))
            else:
                conn.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now, session_id))
            self._append_event_conn(
                conn,
                f"chat.message.{role}",
                "chat",
                session_id,
                actor,
                f"Chat {role} message saved.",
                {"session_id": session_id, "message_id": message_id, "role": role, "provider": provider, "model": model},
                now,
            )
            row = conn.execute("SELECT * FROM chat_messages WHERE id = ?", (message_id,)).fetchone()
        return self._chat_message(row)

    def create_note(self, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        note_id = str(uuid.uuid4())
        now = utc_now()
        title = str(payload.get("title") or "Workstation note").strip()
        body = str(payload.get("body") or "").strip()
        surface = str(payload.get("surface") or "workstation").strip()
        source_id = str(payload.get("source_id") or "").strip()
        tags = payload.get("tags") if isinstance(payload.get("tags"), list) else []
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO notes (id, title, body, surface, source_id, actor, tags_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (note_id, title, body, surface, source_id, actor, _json_dumps(tags), now, now),
            )
            self._append_event_conn(
                conn,
                "note.saved",
                surface,
                source_id or note_id,
                actor,
                f"Note saved: {title}",
                {"note_id": note_id, "surface": surface, "source_id": source_id},
                now,
            )
            row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return self._note(row)

    def update_note(self, note_id: str, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any] | None:
        current = self.get_note(note_id)
        if not current:
            return None
        now = utc_now()
        title = str(payload.get("title", current["title"])).strip()
        body = str(payload.get("body", current["body"])).strip()
        surface = str(payload.get("surface", current["surface"])).strip()
        source_id = str(payload.get("source_id", current["source_id"])).strip()
        tags = payload.get("tags") if isinstance(payload.get("tags"), list) else current["tags"]
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE notes SET title = ?, body = ?, surface = ?, source_id = ?, tags_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (title, body, surface, source_id, _json_dumps(tags), now, note_id),
            )
            self._append_event_conn(
                conn,
                "note.updated",
                surface,
                source_id or note_id,
                actor,
                f"Note updated: {title}",
                {"note_id": note_id, "surface": surface, "source_id": source_id},
                now,
            )
            row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return self._note(row)

    def get_note(self, note_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return self._note(row) if row else None

    def list_notes(self, surface: str | None = None, source_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as conn:
            return self._list_notes_conn(conn, surface=surface, source_id=source_id, limit=limit)

    def create_memory(self, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        memory_id = str(uuid.uuid4())
        now = utc_now()
        content = str(payload.get("content") or payload.get("text") or "").strip()
        if not content:
            raise ValueError("Memory content is required.")
        memory_type = str(payload.get("memory_type") or payload.get("type") or "note").strip()
        source_surface = str(payload.get("source_surface") or payload.get("surface") or "workstation").strip()
        source_id = str(payload.get("source_id") or "").strip()
        tags = payload.get("tags") if isinstance(payload.get("tags"), list) else []
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO memory_entries (id, content, memory_type, source_surface, source_id, actor, tags_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (memory_id, content, memory_type, source_surface, source_id, actor, _json_dumps(tags), now, now),
            )
            self._append_event_conn(
                conn,
                "memory.saved",
                source_surface,
                source_id or memory_id,
                actor,
                "Memory saved.",
                {"memory_id": memory_id, "memory_type": memory_type, "tags": tags},
                now,
            )
            row = conn.execute("SELECT * FROM memory_entries WHERE id = ?", (memory_id,)).fetchone()
        return self._memory(row)

    def list_memory(self, limit: int = 100, tag: str | None = None, memory_type: str | None = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if memory_type:
            clauses.append("memory_type = ?")
            params.append(memory_type)
        sql = "SELECT * FROM memory_entries"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(max(1, min(limit, 500)))
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        memories = [self._memory(row) for row in rows]
        if tag:
            memories = [item for item in memories if tag in item["tags"]]
        return memories

    def recall_memory(self, query: str = "", limit: int = 8, tags: list[str] | None = None) -> list[dict[str, Any]]:
        entries = self.list_memory(limit=500)
        needles = [part.lower() for part in query.split() if part.strip()]
        tag_filter = set(tags or [])

        def score(entry: dict[str, Any]) -> tuple[int, str]:
            haystack = " ".join([entry["content"], entry["memory_type"], " ".join(entry["tags"])]).lower()
            text_score = sum(1 for needle in needles if needle in haystack)
            tag_score = len(tag_filter.intersection(entry["tags"]))
            return (text_score + tag_score, entry["updated_at"])

        if needles or tag_filter:
            entries = [entry for entry in entries if score(entry)[0] > 0]
        entries.sort(key=score, reverse=True)
        return entries[: max(1, min(limit, 50))]

    def delete_memory(self, memory_id: str, actor: str = "operator") -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM memory_entries WHERE id = ?", (memory_id,)).fetchone()
            if not row:
                return False
            conn.execute("DELETE FROM memory_entries WHERE id = ?", (memory_id,))
            self._append_event_conn(
                conn,
                "memory.deleted",
                row["source_surface"],
                row["source_id"] or memory_id,
                actor,
                "Memory deleted.",
                {"memory_id": memory_id},
                utc_now(),
            )
        return True

    def append_event(self, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        now = utc_now()
        with self.connect() as conn:
            return self._append_event_conn(
                conn,
                str(payload.get("event_type") or "workstation.event"),
                str(payload.get("surface") or "workstation"),
                str(payload.get("source_id") or ""),
                actor,
                str(payload.get("summary") or "Workstation event."),
                payload.get("payload") if isinstance(payload.get("payload"), dict) else {},
                now,
            )

    def list_events(self, limit: int = 100, event_type: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM events"
        params: list[Any] = []
        if event_type:
            sql += " WHERE event_type = ?"
            params.append(event_type)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(max(1, min(limit, 500)))
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._event(row) for row in rows]

    def create_confirmation(self, payload: dict[str, Any], actor: str = "operator") -> dict[str, Any]:
        confirmation_id = str(uuid.uuid4())
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()
        ttl_seconds = CONFIRMATION_TTL_SECONDS
        expires_at = (now_dt + timedelta(seconds=ttl_seconds)).isoformat()
        action_type = str(payload.get("action_type") or "workstation.action")
        surface = str(payload.get("surface") or "workstation")
        source_id = str(payload.get("source_id") or "")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO action_confirmations
                  (id, action_type, status, risk_level, prompt, surface, source_id, created_at, expires_at, resolved_at, used_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)
                """,
                (
                    confirmation_id,
                    action_type,
                    "pending",
                    str(payload.get("risk_level") or "confirm"),
                    str(payload.get("prompt") or "Confirm this action before continuing."),
                    surface,
                    source_id,
                    now,
                    expires_at,
                ),
            )
            self._append_event_conn(
                conn,
                "guardian.confirmation_required",
                surface,
                source_id or confirmation_id,
                actor,
                "Action confirmation required.",
                {"confirmation_id": confirmation_id, "action_type": action_type},
                now,
            )
            row = conn.execute("SELECT * FROM action_confirmations WHERE id = ?", (confirmation_id,)).fetchone()
        return self._confirmation(row)

    def list_confirmations(self, limit: int = 50, status: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM action_confirmations"
        params: list[Any] = []
        if status:
            sql += " WHERE status = ?"
            params.append(status)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(max(1, min(limit, 200)))
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._confirmation(row) for row in rows]

    def decide_confirmation(self, confirmation_id: str, decision: str, actor: str = "operator") -> dict[str, Any] | None:
        normalized = decision.strip().lower()
        if normalized not in {"approved", "denied"}:
            raise ValueError("Confirmation decision must be approved or denied.")
        now = utc_now()
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM action_confirmations WHERE id = ?", (confirmation_id,)).fetchone()
            if not row:
                return None
            if row["status"] != "pending":
                return self._confirmation(row)
            conn.execute(
                "UPDATE action_confirmations SET status = ?, resolved_at = ? WHERE id = ?",
                (normalized, now, confirmation_id),
            )
            event_type = "guardian.confirmation_approved" if normalized == "approved" else "guardian.confirmation_denied"
            self._append_event_conn(
                conn,
                event_type,
                row["surface"],
                row["source_id"] or confirmation_id,
                actor,
                f"Action confirmation {normalized}.",
                {"confirmation_id": confirmation_id, "action_type": row["action_type"]},
                now,
            )
            row = conn.execute("SELECT * FROM action_confirmations WHERE id = ?", (confirmation_id,)).fetchone()
        return self._confirmation(row)

    def authorize_action(
        self,
        confirmation_id: str | None,
        action_type: str,
        surface: str,
        source_id: str,
        actor: str = "operator",
    ) -> tuple[bool, str]:
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()
        clean_confirmation_id = str(confirmation_id or "").strip()

        def block(conn: sqlite3.Connection, reason: str, row: sqlite3.Row | None = None) -> tuple[bool, str]:
            conn_surface = row["surface"] if row else surface
            conn_source_id = row["source_id"] if row else source_id
            self._append_event_conn(
                conn,
                "guardian.action_blocked",
                conn_surface,
                conn_source_id or clean_confirmation_id,
                actor,
                reason,
                {
                    "confirmation_id": clean_confirmation_id,
                    "expected_action_type": action_type,
                    "expected_surface": surface,
                    "expected_source_id": source_id,
                    "reason": reason,
                },
                now,
            )
            return False, reason

        with self.connect() as conn:
            if not clean_confirmation_id:
                return block(conn, "Guardian confirmation required.")
            row = conn.execute("SELECT * FROM action_confirmations WHERE id = ?", (clean_confirmation_id,)).fetchone()
            if not row:
                return block(conn, "Guardian confirmation was not found.")
            if row["used_at"] or row["status"] == "used":
                return block(conn, "Guardian confirmation was already used.", row)
            if row["status"] == "denied":
                return block(conn, "Guardian confirmation was denied.", row)
            if row["status"] != "approved":
                return block(conn, "Guardian confirmation is not approved.", row)
            expires_at = _parse_utc(row["expires_at"])
            if not expires_at or expires_at <= now_dt:
                conn.execute(
                    "UPDATE action_confirmations SET status = ?, resolved_at = COALESCE(resolved_at, ?) WHERE id = ?",
                    ("expired", now, clean_confirmation_id),
                )
                return block(conn, "Guardian confirmation expired.", row)
            if row["action_type"] != action_type or row["surface"] != surface or row["source_id"] != source_id:
                return block(conn, "Guardian confirmation does not match this action.", row)
            conn.execute(
                "UPDATE action_confirmations SET status = ?, used_at = ? WHERE id = ?",
                ("used", now, clean_confirmation_id),
            )
            self._append_event_conn(
                conn,
                "guardian.action_authorized",
                surface,
                source_id,
                actor,
                "Guardian confirmation authorized an action.",
                {"confirmation_id": clean_confirmation_id, "action_type": action_type},
                now,
            )
        return True, "Guardian confirmation accepted."

    def workstation_state(self) -> dict[str, Any]:
        seats = self.list_seats()
        rooms = self.list_rooms(limit=10)
        notes = self.list_notes(limit=10)
        memories = self.list_memory(limit=10)
        events = self.list_events(limit=20)
        return {
            "seats": seats,
            "rooms": rooms,
            "notes": notes,
            "memory": {"items": memories, "count": self.count("memory_entries")},
            "events": events,
            "chat": {
                "sessions": self.list_chat_sessions(limit=10),
                "sessions_count": self.count("chat_sessions"),
                "messages_count": self.count("chat_messages"),
            },
            "guardian": {
                "pending_confirmations": self.list_confirmations(limit=20, status="pending"),
                "recent_confirmations": self.list_confirmations(limit=20),
            },
            "dashboard": self.dashboard_summary(),
            "storage": {"type": "sqlite", "path": "local-workstation-store"},
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return {
            "rooms_count": self.count("rooms"),
            "notes_count": self.count("notes"),
            "memory_count": self.count("memory_entries"),
            "events_count": self.count("events"),
            "seat_count": self.count("seats"),
            "chat_sessions_count": self.count("chat_sessions"),
            "chat_messages_count": self.count("chat_messages"),
            "pending_confirmations": self.count("action_confirmations", "status = 'pending'"),
        }

    def count(self, table: str, where: str = "") -> int:
        allowed = {"rooms", "notes", "memory_entries", "events", "seats", "action_confirmations", "chat_sessions", "chat_messages"}
        if table not in allowed:
            raise ValueError("Unsupported table.")
        sql = f"SELECT COUNT(*) AS count FROM {table}"
        if where:
            sql += f" WHERE {where}"
        with self.connect() as conn:
            return int(conn.execute(sql).fetchone()["count"])

    def _list_seats_conn(self, conn: sqlite3.Connection) -> list[dict[str, Any]]:
        rows = conn.execute("SELECT * FROM seats ORDER BY seat_index").fetchall()
        return [self._seat(row) for row in rows]

    def _list_room_participants_conn(self, conn: sqlite3.Connection, room_id: str) -> list[dict[str, Any]]:
        rows = conn.execute(
            "SELECT * FROM room_participants WHERE room_id = ? ORDER BY seat_index, created_at",
            (room_id,),
        ).fetchall()
        return [self._participant(row) for row in rows]

    def _list_chat_messages_conn(self, conn: sqlite3.Connection, session_id: str) -> list[dict[str, Any]]:
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ).fetchall()
        return [self._chat_message(row) for row in rows]

    def _last_chat_message_conn(self, conn: sqlite3.Connection, session_id: str) -> dict[str, Any] | None:
        row = conn.execute(
            "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        return self._chat_message(row) if row else None

    def _list_notes_conn(
        self,
        conn: sqlite3.Connection,
        surface: str | None = None,
        source_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if surface:
            clauses.append("surface = ?")
            params.append(surface)
        if source_id:
            clauses.append("source_id = ?")
            params.append(source_id)
        sql = "SELECT * FROM notes"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(max(1, min(limit, 200)))
        rows = conn.execute(sql, params).fetchall()
        return [self._note(row) for row in rows]

    def _append_event_conn(
        self,
        conn: sqlite3.Connection,
        event_type: str,
        surface: str,
        source_id: str,
        actor: str,
        summary: str,
        payload: dict[str, Any],
        created_at: str,
    ) -> dict[str, Any]:
        event_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO events (id, event_type, surface, source_id, actor, summary, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (event_id, event_type, surface, source_id, actor, summary, _json_dumps(_sanitize_payload(payload)), created_at),
        )
        row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        return self._event(row)

    def _seat(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "seat_index": int(row["seat_index"]),
            "label": row["label"],
            "agent": row["agent"],
            "provider": row["provider"],
            "model": row["model"],
            "updated_at": row["updated_at"],
        }

    def _room(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "status": row["status"],
            "phase": row["phase"],
            "goal": row["goal"],
            "summary": row["summary"],
            "metadata": _json_loads(row["metadata_json"], {}),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _participant(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "room_id": row["room_id"],
            "seat_index": row["seat_index"],
            "agent": row["agent"],
            "provider": row["provider"],
            "model": row["model"],
            "role": row["role"],
            "created_at": row["created_at"],
        }

    def _chat_session(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "status": row["status"],
            "active_room_id": row["active_room_id"],
            "metadata": _json_loads(row["metadata_json"], {}),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _chat_message(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "role": row["role"],
            "content": row["content"],
            "actor": row["actor"],
            "provider": row["provider"],
            "model": row["model"],
            "metadata": _json_loads(row["metadata_json"], {}),
            "created_at": row["created_at"],
        }

    def _note(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "body": row["body"],
            "surface": row["surface"],
            "source_id": row["source_id"],
            "actor": row["actor"],
            "tags": _json_loads(row["tags_json"], []),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _memory(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "content": row["content"],
            "memory_type": row["memory_type"],
            "source_surface": row["source_surface"],
            "source_id": row["source_id"],
            "actor": row["actor"],
            "tags": _json_loads(row["tags_json"], []),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _event(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "event_type": row["event_type"],
            "surface": row["surface"],
            "source_id": row["source_id"],
            "actor": row["actor"],
            "summary": row["summary"],
            "payload": _json_loads(row["payload_json"], {}),
            "created_at": row["created_at"],
        }

    def _confirmation(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "action_type": row["action_type"],
            "status": row["status"],
            "risk_level": row["risk_level"],
            "prompt": row["prompt"],
            "surface": row["surface"],
            "source_id": row["source_id"],
            "created_at": row["created_at"],
            "expires_at": row["expires_at"],
            "resolved_at": row["resolved_at"],
            "used_at": row["used_at"],
        }


def get_store() -> WorkstationStore:
    return WorkstationStore()
