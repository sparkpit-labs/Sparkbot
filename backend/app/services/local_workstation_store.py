from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

DATABASE_NAME = "sparkbot_public.sqlite3"
ALLOWED_MESSAGE_ROLES = {"operator", "note", "assistant-local"}
ALLOWED_WORK_LANES = {"inbox", "planned", "active", "review", "done"}
ALLOWED_CARD_STATUSES = {"open", "in-progress", "blocked", "done"}
_UNCHANGED = object()


class LocalStoreError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id() -> str:
    return uuid4().hex


def default_data_dir() -> Path:
    configured = os.environ.get("SPARKBOT_DATA_DIR", "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".local" / "share" / "sparkbot-public"


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


class LocalWorkstationStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or default_data_dir()
        self.database_path = self.data_dir / DATABASE_NAME
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS memory_notes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'operator',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS work_lane_cards (
                    id TEXT PRIMARY KEY,
                    lane TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    chat_session_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (chat_session_id) REFERENCES chat_sessions(id) ON DELETE SET NULL
                );
                """
            )
            self._ensure_work_lane_chat_link_column(connection)

    def export_local_data(self) -> dict[str, Any]:
        return {
            "service": "sparkbot-server",
            "mode": "local",
            "export_type": "local-workstation-data",
            "schema_version": 1,
            "exported_at": utc_now(),
            "import_supported": False,
            "cloud_sync": "not-supported",
            "external_upload": "not-supported",
            "data": {
                "chat_sessions": self._export_chat_sessions(),
                "memory_notes": self.list_memory_notes(),
                "work_lane_cards": self.list_work_lane_cards(),
            },
        }

    def list_chat_sessions(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT chat_sessions.*, COUNT(chat_messages.id) AS message_count
                FROM chat_sessions
                LEFT JOIN chat_messages ON chat_messages.session_id = chat_sessions.id
                GROUP BY chat_sessions.id
                ORDER BY updated_at DESC, created_at DESC
                """
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def create_chat_session(self, title: str) -> dict[str, Any]:
        title = _require_text(title, "title")
        now = utc_now()
        session = {"id": new_id(), "title": title, "created_at": now, "updated_at": now}
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO chat_sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session["id"], session["title"], session["created_at"], session["updated_at"]),
            )
        return {**session, "messages": []}

    def get_chat_session(self, session_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            session = connection.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
            if session is None:
                raise NotFoundError("Chat session not found")
            messages = connection.execute(
                "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,),
            ).fetchall()
        return {**_row_to_dict(session), "messages": [_row_to_dict(row) for row in messages]}

    def update_chat_session(self, session_id: str, title: str) -> dict[str, Any]:
        title = _require_text(title, "title")
        now = utc_now()
        with self.connect() as connection:
            cursor = connection.execute(
                "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, session_id),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Chat session not found")
        return self.get_chat_session(session_id)

    def delete_chat_session(self, session_id: str) -> None:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            if cursor.rowcount == 0:
                raise NotFoundError("Chat session not found")
            connection.execute("UPDATE work_lane_cards SET chat_session_id = NULL, updated_at = ? WHERE chat_session_id = ?", (utc_now(), session_id))

    def add_chat_message(self, session_id: str, role: str, content: str) -> dict[str, Any]:
        role = _require_allowed(role, ALLOWED_MESSAGE_ROLES, "role")
        content = _require_text(content, "content")
        now = utc_now()
        message = {"id": new_id(), "session_id": session_id, "role": role, "content": content, "created_at": now}
        with self.connect() as connection:
            session = connection.execute("SELECT id FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
            if session is None:
                raise NotFoundError("Chat session not found")
            connection.execute(
                "INSERT INTO chat_messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (message["id"], message["session_id"], message["role"], message["content"], message["created_at"]),
            )
            connection.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now, session_id))
        return message

    def list_memory_notes(self) -> list[dict[str, Any]]:
        return self._list_rows("memory_notes", "updated_at DESC, created_at DESC")

    def create_memory_note(self, title: str, body: str, source: str = "operator") -> dict[str, Any]:
        title = _require_text(title, "title")
        body = _require_text(body, "body")
        source = _require_text(source or "operator", "source")
        now = utc_now()
        note = {"id": new_id(), "title": title, "body": body, "source": source, "created_at": now, "updated_at": now}
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO memory_notes (id, title, body, source, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (note["id"], note["title"], note["body"], note["source"], note["created_at"], note["updated_at"]),
            )
        return note

    def get_memory_note(self, note_id: str) -> dict[str, Any]:
        return self._get_row("memory_notes", note_id, "Memory note not found")

    def update_memory_note(self, note_id: str, title: str | None = None, body: str | None = None, source: str | None = None) -> dict[str, Any]:
        current = self.get_memory_note(note_id)
        title = _require_text(title if title is not None else current["title"], "title")
        body = _require_text(body if body is not None else current["body"], "body")
        source = _require_text(source if source is not None else current["source"], "source")
        now = utc_now()
        with self.connect() as connection:
            connection.execute(
                "UPDATE memory_notes SET title = ?, body = ?, source = ?, updated_at = ? WHERE id = ?",
                (title, body, source, now, note_id),
            )
        return self.get_memory_note(note_id)

    def delete_memory_note(self, note_id: str) -> None:
        self._delete_row("memory_notes", note_id, "Memory note not found")

    def list_work_lane_cards(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(_work_lane_card_select_sql("ORDER BY work_lane_cards.updated_at DESC, work_lane_cards.created_at DESC")).fetchall()
        return [_row_to_dict(row) for row in rows]

    def create_work_lane_card(self, lane: str, title: str, body: str, status: str = "open", chat_session_id: str | None = None) -> dict[str, Any]:
        lane = _require_allowed(lane, ALLOWED_WORK_LANES, "lane")
        status = _require_allowed(status, ALLOWED_CARD_STATUSES, "status")
        title = _require_text(title, "title")
        body = _require_text(body, "body")
        chat_session_id = _normalize_optional_id(chat_session_id, "chat_session_id")
        now = utc_now()
        card = {
            "id": new_id(),
            "lane": lane,
            "title": title,
            "body": body,
            "status": status,
            "chat_session_id": chat_session_id,
            "created_at": now,
            "updated_at": now,
        }
        with self.connect() as connection:
            if chat_session_id is not None:
                self._require_chat_session_exists(connection, chat_session_id)
            connection.execute(
                """
                INSERT INTO work_lane_cards (id, lane, title, body, status, chat_session_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    card["id"],
                    card["lane"],
                    card["title"],
                    card["body"],
                    card["status"],
                    card["chat_session_id"],
                    card["created_at"],
                    card["updated_at"],
                ),
            )
        return self.get_work_lane_card(card["id"])

    def get_work_lane_card(self, card_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(_work_lane_card_select_sql("WHERE work_lane_cards.id = ?"), (card_id,)).fetchone()
        if row is None:
            raise NotFoundError("Work lane card not found")
        return _row_to_dict(row)

    def update_work_lane_card(
        self,
        card_id: str,
        lane: str | None = None,
        title: str | None = None,
        body: str | None = None,
        status: str | None = None,
        chat_session_id: str | None | object = _UNCHANGED,
    ) -> dict[str, Any]:
        current = self.get_work_lane_card(card_id)
        lane = _require_allowed(lane if lane is not None else current["lane"], ALLOWED_WORK_LANES, "lane")
        status = _require_allowed(status if status is not None else current["status"], ALLOWED_CARD_STATUSES, "status")
        title = _require_text(title if title is not None else current["title"], "title")
        body = _require_text(body if body is not None else current["body"], "body")
        next_chat_session_id = current["chat_session_id"] if chat_session_id is _UNCHANGED else _normalize_optional_id(chat_session_id, "chat_session_id")
        now = utc_now()
        with self.connect() as connection:
            if next_chat_session_id is not None:
                self._require_chat_session_exists(connection, next_chat_session_id)
            connection.execute(
                "UPDATE work_lane_cards SET lane = ?, title = ?, body = ?, status = ?, chat_session_id = ?, updated_at = ? WHERE id = ?",
                (lane, title, body, status, next_chat_session_id, now, card_id),
            )
        return self.get_work_lane_card(card_id)

    def delete_work_lane_card(self, card_id: str) -> None:
        self._delete_row("work_lane_cards", card_id, "Work lane card not found")

    def _export_chat_sessions(self) -> list[dict[str, Any]]:
        sessions = self.list_chat_sessions()
        return [self.get_chat_session(session["id"]) for session in sessions]

    def _ensure_work_lane_chat_link_column(self, connection: sqlite3.Connection) -> None:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(work_lane_cards)").fetchall()}
        if "chat_session_id" not in columns:
            connection.execute("ALTER TABLE work_lane_cards ADD COLUMN chat_session_id TEXT")

    def _require_chat_session_exists(self, connection: sqlite3.Connection, session_id: str) -> None:
        row = connection.execute("SELECT id FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise NotFoundError("Chat session not found")

    def _list_rows(self, table: str, order_by: str) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
        return [_row_to_dict(row) for row in rows]

    def _get_row(self, table: str, row_id: str, not_found_message: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,)).fetchone()
        if row is None:
            raise NotFoundError(not_found_message)
        return _row_to_dict(row)

    def _delete_row(self, table: str, row_id: str, not_found_message: str) -> None:
        with self.connect() as connection:
            cursor = connection.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
            if cursor.rowcount == 0:
                raise NotFoundError(not_found_message)


def _require_text(value: str, field_name: str) -> str:
    value = value.strip()
    if not value:
        raise LocalStoreError(f"{field_name} is required")
    return value


def _require_allowed(value: str, allowed: Iterable[str], field_name: str) -> str:
    value = value.strip()
    if value not in set(allowed):
        allowed_text = ", ".join(sorted(allowed))
        raise LocalStoreError(f"{field_name} must be one of: {allowed_text}")
    return value


def _normalize_optional_id(value: str | None | object, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise LocalStoreError(f"{field_name} must be a string or null")
    value = value.strip()
    if not value:
        return None
    return value


def _work_lane_card_select_sql(suffix: str = "") -> str:
    return f"""
        SELECT
            work_lane_cards.*,
            chat_sessions.title AS linked_chat_session_title
        FROM work_lane_cards
        LEFT JOIN chat_sessions ON chat_sessions.id = work_lane_cards.chat_session_id
        {suffix}
    """
