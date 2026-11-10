"""Local Roundtable rooms: people and AI agents in one room on this computer.

Storage is the same local SQLite file as the workstation store. Sparkbot
never calls a model here. An agent takes part through a *seat*: the owner
creates a seat, gets a one-time key, and a runner on this computer (started
by the owner) uses that key to pick up @mention jobs and post replies.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.services.local_workstation_store import DATABASE_NAME, default_data_dir, new_id

LEASE_SECONDS = 600
MAX_ATTEMPTS = 2
CONTEXT_MESSAGES = 30
CONTEXT_MESSAGE_CHARS = 4000
MAX_MESSAGE_CHARS = 8000
ONLINE_SECONDS = 60
DEFAULT_JOBS_PER_HOUR = 12
SEAT_KEY_PREFIX = "rts_"
MENTION = re.compile(r"(?<![\w@])@([a-z0-9][a-z0-9-]{1,30})(?![\w-])")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,30}$")
RESERVED_SLUGS = {"all", "owner", "system", "everyone", "here"}


class RoundtableError(ValueError):
    pass


class RoundtableNotFound(LookupError):
    pass


class JobConflict(Exception):
    """The claim is stale, or the job was cancelled or already finished."""

    def __init__(self, message: str, job_status: str) -> None:
        super().__init__(message)
        self.job_status = job_status


def _now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _hash(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def jobs_per_hour() -> int:
    raw = os.environ.get("SPARKBOT_ROUNDTABLE_JOBS_PER_HOUR", "").strip()
    try:
        value = int(raw) if raw else DEFAULT_JOBS_PER_HOUR
    except ValueError:
        return DEFAULT_JOBS_PER_HOUR
    return max(1, min(value, 120))


def _text(value: str, field: str, limit: int) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise RoundtableError(f"{field} is required")
    if len(cleaned) > limit:
        raise RoundtableError(f"{field} is longer than {limit} characters")
    return cleaned


class RoundtableStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or default_data_dir()
        self.database_path = self.data_dir / DATABASE_NAME
        self.initialize()

    # -- plumbing -----------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        """One write transaction. BEGIN IMMEDIATE takes the write lock up front,
        so read-then-update steps (claim, complete) cannot interleave."""
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    @contextmanager
    def _read(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._read() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS roundtable_rooms (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    paused INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS roundtable_seats (
                    id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT,
                    FOREIGN KEY (room_id) REFERENCES roundtable_rooms(id) ON DELETE CASCADE,
                    UNIQUE (room_id, slug)
                );

                CREATE TABLE IF NOT EXISTS roundtable_messages (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT NOT NULL UNIQUE,
                    room_id TEXT NOT NULL,
                    sender_kind TEXT NOT NULL,
                    seat_id TEXT,
                    sender_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    reply_to_id TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (room_id) REFERENCES roundtable_rooms(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS roundtable_messages_room
                    ON roundtable_messages (room_id, seq);

                CREATE TABLE IF NOT EXISTS roundtable_jobs (
                    id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    seat_id TEXT NOT NULL,
                    trigger_message_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reason TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    claim_hash TEXT,
                    lease_expires_at TEXT,
                    note TEXT,
                    reply_message_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (room_id) REFERENCES roundtable_rooms(id) ON DELETE CASCADE,
                    FOREIGN KEY (seat_id) REFERENCES roundtable_seats(id) ON DELETE CASCADE,
                    UNIQUE (seat_id, trigger_message_id)
                );
                """
            )

    # -- rooms --------------------------------------------------------------

    def list_rooms(self) -> list[dict[str, Any]]:
        with self._read() as connection:
            rows = connection.execute(
                """
                SELECT r.*, (SELECT COUNT(*) FROM roundtable_seats s WHERE s.room_id = r.id) AS seat_count
                FROM roundtable_rooms r ORDER BY r.updated_at DESC, r.created_at DESC
                """
            ).fetchall()
        return [self._room_dict(row) for row in rows]

    def create_room(self, name: str) -> dict[str, Any]:
        name = _text(name, "name", 120)
        now = _iso(_now())
        room_id = new_id()
        with self._tx() as connection:
            connection.execute(
                "INSERT INTO roundtable_rooms (id, name, paused, created_at, updated_at) VALUES (?, ?, 0, ?, ?)",
                (room_id, name, now, now),
            )
        return self.get_room(room_id)

    def get_room(self, room_id: str) -> dict[str, Any]:
        with self._read() as connection:
            row = connection.execute(
                """
                SELECT r.*, (SELECT COUNT(*) FROM roundtable_seats s WHERE s.room_id = r.id) AS seat_count
                FROM roundtable_rooms r WHERE r.id = ?
                """,
                (room_id,),
            ).fetchone()
        if row is None:
            raise RoundtableNotFound("Room not found")
        return self._room_dict(row)

    def delete_room(self, room_id: str) -> None:
        with self._tx() as connection:
            if connection.execute("DELETE FROM roundtable_rooms WHERE id = ?", (room_id,)).rowcount == 0:
                raise RoundtableNotFound("Room not found")

    @staticmethod
    def _room_dict(row: sqlite3.Row) -> dict[str, Any]:
        room = dict(row)
        room["paused"] = bool(room["paused"])
        return room

    # -- seats --------------------------------------------------------------

    def create_seat(self, room_id: str, display_name: str, slug: str) -> dict[str, Any]:
        display_name = _text(display_name, "display_name", 60)
        slug = (slug or "").strip().lower()
        if not SLUG.match(slug) or slug in RESERVED_SLUGS:
            raise RoundtableError("slug must be 2-31 lowercase letters, digits or '-', and not a reserved word")
        self.get_room(room_id)
        seat_id = new_id()
        secret = secrets.token_urlsafe(32)
        now = _iso(_now())
        try:
            with self._tx() as connection:
                connection.execute(
                    """
                    INSERT INTO roundtable_seats (id, room_id, slug, display_name, key_hash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (seat_id, room_id, slug, display_name, _hash(secret), now),
                )
                self._touch_room(connection, room_id, now)
        except sqlite3.IntegrityError as error:
            raise RoundtableError(f"@{slug} is already in this room") from error
        seat = self.get_seat(room_id, seat_id)
        return {**seat, "key": f"{SEAT_KEY_PREFIX}{seat_id}_{secret}"}

    def rotate_seat_key(self, room_id: str, seat_id: str) -> dict[str, Any]:
        secret = secrets.token_urlsafe(32)
        with self._tx() as connection:
            updated = connection.execute(
                "UPDATE roundtable_seats SET key_hash = ? WHERE id = ? AND room_id = ?",
                (_hash(secret), seat_id, room_id),
            ).rowcount
            if updated == 0:
                raise RoundtableNotFound("Seat not found")
        return {**self.get_seat(room_id, seat_id), "key": f"{SEAT_KEY_PREFIX}{seat_id}_{secret}"}

    def delete_seat(self, room_id: str, seat_id: str) -> None:
        with self._tx() as connection:
            if connection.execute(
                "DELETE FROM roundtable_seats WHERE id = ? AND room_id = ?", (seat_id, room_id)
            ).rowcount == 0:
                raise RoundtableNotFound("Seat not found")

    def get_seat(self, room_id: str, seat_id: str) -> dict[str, Any]:
        seats = [seat for seat in self.list_seats(room_id) if seat["id"] == seat_id]
        if not seats:
            raise RoundtableNotFound("Seat not found")
        return seats[0]

    def list_seats(self, room_id: str) -> list[dict[str, Any]]:
        self.get_room(room_id)
        now = _now()
        with self._read() as connection:
            rows = connection.execute(
                """
                SELECT s.id, s.room_id, s.slug, s.display_name, s.created_at, s.last_seen_at,
                    (SELECT COUNT(*) FROM roundtable_jobs j WHERE j.seat_id = s.id AND j.status = 'pending') AS pending_jobs,
                    (SELECT j.note FROM roundtable_jobs j WHERE j.seat_id = s.id AND j.status = 'claimed'
                        ORDER BY j.updated_at DESC LIMIT 1) AS working_note,
                    (SELECT COUNT(*) FROM roundtable_jobs j WHERE j.seat_id = s.id AND j.status = 'claimed') AS claimed_jobs
                FROM roundtable_seats s WHERE s.room_id = ? ORDER BY s.created_at ASC, s.rowid ASC
                """,
                (room_id,),
            ).fetchall()
        seats = []
        for row in rows:
            seat = dict(row)
            claimed = seat.pop("claimed_jobs")
            seen = seat["last_seen_at"]
            online = bool(seen) and (now - _parse(seen)).total_seconds() <= ONLINE_SECONDS
            seat["presence"] = "working" if claimed else ("online" if online else "offline")
            seats.append(seat)
        return seats

    def authenticate_seat(self, key: str) -> dict[str, Any] | None:
        """Return the seat for a key, or None. Constant-time compare on the hash."""
        if not key or not key.startswith(SEAT_KEY_PREFIX):
            return None
        seat_id, _, secret = key[len(SEAT_KEY_PREFIX):].partition("_")
        if not seat_id or not secret:
            return None
        with self._tx() as connection:
            row = connection.execute(
                """
                SELECT s.*, r.name AS room_name FROM roundtable_seats s
                JOIN roundtable_rooms r ON r.id = s.room_id WHERE s.id = ?
                """,
                (seat_id,),
            ).fetchone()
            if row is None or not hmac.compare_digest(row["key_hash"], _hash(secret)):
                return None
            connection.execute(
                "UPDATE roundtable_seats SET last_seen_at = ? WHERE id = ?", (_iso(_now()), seat_id)
            )
        seat = dict(row)
        seat.pop("key_hash")
        return seat

    # -- messages -----------------------------------------------------------

    def list_messages(self, room_id: str, after: int = 0, limit: int = 200) -> list[dict[str, Any]]:
        self.get_room(room_id)
        limit = max(1, min(limit, 500))
        with self._read() as connection:
            if after > 0:
                rows = connection.execute(
                    "SELECT * FROM roundtable_messages WHERE room_id = ? AND seq > ? ORDER BY seq ASC LIMIT ?",
                    (room_id, after, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT * FROM (
                        SELECT * FROM roundtable_messages WHERE room_id = ? ORDER BY seq DESC LIMIT ?
                    ) ORDER BY seq ASC
                    """,
                    (room_id, limit),
                ).fetchall()
        return [dict(row) for row in rows]

    def post_owner_message(self, room_id: str, content: str, sender_name: str = "Owner") -> dict[str, Any]:
        """A human message from the room owner. Handles /pause, /resume and @mentions."""
        content = _text(content, "content", MAX_MESSAGE_CHARS)
        command = content.lower()
        with self._tx() as connection:
            room = connection.execute("SELECT * FROM roundtable_rooms WHERE id = ?", (room_id,)).fetchone()
            if room is None:
                raise RoundtableNotFound("Room not found")
            message = self._insert_message(connection, room_id, "owner", None, sender_name[:60], content, None)
            notices: list[str] = []
            if command == "/pause":
                cancelled = self._set_paused(connection, room_id, True)
                notices.append(f"Room paused. Agents get no new work. Cancelled {cancelled} open job(s). Post /resume to continue.")
            elif command == "/resume":
                self._set_paused(connection, room_id, False)
                notices.append("Room resumed. @mentions wake agents again.")
            elif room["paused"]:
                if MENTION.search(content):
                    notices.append("Room is paused, so no agent was woken. Post /resume first.")
            else:
                notices.extend(self._create_jobs(connection, room_id, message))
            for notice in notices:
                self._insert_message(connection, room_id, "system", None, "Roundtable", notice, message["id"])
        return message

    def post_seat_message(self, seat: dict[str, Any], content: str, reply_to_id: str | None) -> dict[str, Any]:
        """An agent's own post (for example from MCP). Agent posts never wake agents."""
        content = _text(content, "content", MAX_MESSAGE_CHARS)
        with self._tx() as connection:
            if reply_to_id:
                self._require_message(connection, seat["room_id"], reply_to_id)
            return self._insert_message(
                connection, seat["room_id"], "agent", seat["id"], seat["display_name"], content, reply_to_id
            )

    def _require_message(self, connection: sqlite3.Connection, room_id: str, message_id: str) -> None:
        row = connection.execute(
            "SELECT 1 FROM roundtable_messages WHERE id = ? AND room_id = ?", (message_id, room_id)
        ).fetchone()
        if row is None:
            raise RoundtableError("reply_to_id is not a message in this room")

    def _insert_message(
        self,
        connection: sqlite3.Connection,
        room_id: str,
        sender_kind: str,
        seat_id: str | None,
        sender_name: str,
        content: str,
        reply_to_id: str | None,
    ) -> dict[str, Any]:
        now = _iso(_now())
        message_id = new_id()
        cursor = connection.execute(
            """
            INSERT INTO roundtable_messages (id, room_id, sender_kind, seat_id, sender_name, content, reply_to_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (message_id, room_id, sender_kind, seat_id, sender_name, content, reply_to_id, now),
        )
        self._touch_room(connection, room_id, now)
        return {
            "seq": cursor.lastrowid,
            "id": message_id,
            "room_id": room_id,
            "sender_kind": sender_kind,
            "seat_id": seat_id,
            "sender_name": sender_name,
            "content": content,
            "reply_to_id": reply_to_id,
            "created_at": now,
        }

    @staticmethod
    def _touch_room(connection: sqlite3.Connection, room_id: str, now: str) -> None:
        connection.execute("UPDATE roundtable_rooms SET updated_at = ? WHERE id = ?", (now, room_id))

    # -- pause --------------------------------------------------------------

    def set_paused(self, room_id: str, paused: bool) -> dict[str, Any]:
        with self._tx() as connection:
            if connection.execute("SELECT 1 FROM roundtable_rooms WHERE id = ?", (room_id,)).fetchone() is None:
                raise RoundtableNotFound("Room not found")
            self._set_paused(connection, room_id, paused)
        return self.get_room(room_id)

    def _set_paused(self, connection: sqlite3.Connection, room_id: str, paused: bool) -> int:
        now = _iso(_now())
        connection.execute(
            "UPDATE roundtable_rooms SET paused = ?, updated_at = ? WHERE id = ?", (int(paused), now, room_id)
        )
        if not paused:
            return 0
        return connection.execute(
            """
            UPDATE roundtable_jobs SET status = 'cancelled', reason = 'paused', updated_at = ?
            WHERE room_id = ? AND status IN ('pending', 'claimed')
            """,
            (now, room_id),
        ).rowcount

    # -- jobs ---------------------------------------------------------------

    def _create_jobs(self, connection: sqlite3.Connection, room_id: str, message: dict[str, Any]) -> list[str]:
        slugs = set(MENTION.findall(message["content"].lower()))
        if not slugs:
            return []
        seats = connection.execute(
            "SELECT id, slug, display_name FROM roundtable_seats WHERE room_id = ? ORDER BY created_at, rowid", (room_id,)
        ).fetchall()
        targets = seats if "all" in slugs else [seat for seat in seats if seat["slug"] in slugs]
        now = _now()
        hour_ago = _iso(now - timedelta(hours=1))
        cap = jobs_per_hour()
        notices = []
        for seat in targets:
            recent = connection.execute(
                "SELECT COUNT(*) FROM roundtable_jobs WHERE seat_id = ? AND created_at > ? AND status != 'skipped'",
                (seat["id"], hour_ago),
            ).fetchone()[0]
            job_status, reason = ("pending", None) if recent < cap else ("skipped", "hourly cap")
            connection.execute(
                """
                INSERT OR IGNORE INTO roundtable_jobs
                    (id, room_id, seat_id, trigger_message_id, status, reason, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (new_id(), room_id, seat["id"], message["id"], job_status, reason, _iso(now), _iso(now)),
            )
            if job_status == "skipped":
                notices.append(f"@{seat['slug']} reached its limit of {cap} answers per hour, so it was not woken.")
        return notices

    def _expire_leases(self, connection: sqlite3.Connection, seat_id: str) -> None:
        now = _iso(_now())
        connection.execute(
            """
            UPDATE roundtable_jobs
            SET status = CASE WHEN attempts >= ? THEN 'expired' ELSE 'pending' END,
                claim_hash = NULL, note = NULL, updated_at = ?
            WHERE seat_id = ? AND status = 'claimed' AND lease_expires_at < ?
            """,
            (MAX_ATTEMPTS, now, seat_id, now),
        )

    def claim_next(self, seat: dict[str, Any]) -> dict[str, Any] | None:
        token = secrets.token_urlsafe(24)
        now = _now()
        lease = _iso(now + timedelta(seconds=LEASE_SECONDS))
        with self._tx() as connection:
            self._expire_leases(connection, seat["id"])
            room = connection.execute(
                "SELECT * FROM roundtable_rooms WHERE id = ?", (seat["room_id"],)
            ).fetchone()
            if room is None or room["paused"]:
                return None
            row = connection.execute(
                """
                SELECT * FROM roundtable_jobs WHERE seat_id = ? AND status = 'pending'
                ORDER BY created_at ASC, rowid ASC LIMIT 1
                """,
                (seat["id"],),
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                """
                UPDATE roundtable_jobs SET status = 'claimed', attempts = attempts + 1, claim_hash = ?,
                    lease_expires_at = ?, note = NULL, updated_at = ?
                WHERE id = ?
                """,
                (_hash(token), lease, _iso(now), row["id"]),
            )
            trigger = connection.execute(
                "SELECT * FROM roundtable_messages WHERE id = ?", (row["trigger_message_id"],)
            ).fetchone()
            context = connection.execute(
                """
                SELECT * FROM (
                    SELECT * FROM roundtable_messages WHERE room_id = ? AND seq <= ? ORDER BY seq DESC LIMIT ?
                ) ORDER BY seq ASC
                """,
                (seat["room_id"], trigger["seq"], CONTEXT_MESSAGES),
            ).fetchall()
        return {
            "id": row["id"],
            "claim_token": token,
            "room": {"id": room["id"], "name": room["name"]},
            "trigger": self._public_message(trigger),
            "context": [self._public_message(item) for item in context],
            "lease_expires_at": lease,
            "attempt": row["attempts"] + 1,
            "limits": {
                "max_reply_chars": MAX_MESSAGE_CHARS,
                "lease_seconds": LEASE_SECONDS,
                "context_messages": CONTEXT_MESSAGES,
                "context_message_chars": CONTEXT_MESSAGE_CHARS,
            },
        }

    @staticmethod
    def _public_message(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "sender_name": row["sender_name"],
            "sender_type": "HUMAN" if row["sender_kind"] == "owner" else ("BOT" if row["sender_kind"] == "agent" else "SYSTEM"),
            "content": row["content"][:CONTEXT_MESSAGE_CHARS],
            "created_at": row["created_at"],
        }

    def _claimed_job(self, connection: sqlite3.Connection, seat: dict[str, Any], job_id: str, token: str) -> sqlite3.Row:
        self._expire_leases(connection, seat["id"])
        row = connection.execute(
            "SELECT * FROM roundtable_jobs WHERE id = ? AND seat_id = ?", (job_id, seat["id"])
        ).fetchone()
        if row is None:
            raise RoundtableNotFound("Job not found")
        if row["status"] != "claimed" or not row["claim_hash"] or not hmac.compare_digest(row["claim_hash"], _hash(token or "")):
            raise JobConflict("This claim is no longer valid", row["status"])
        return row

    def heartbeat(self, seat: dict[str, Any], job_id: str, token: str, note: str | None) -> dict[str, Any]:
        now = _now()
        with self._tx() as connection:
            self._claimed_job(connection, seat, job_id, token)
            lease = _iso(now + timedelta(seconds=LEASE_SECONDS))
            connection.execute(
                "UPDATE roundtable_jobs SET lease_expires_at = ?, note = ?, updated_at = ? WHERE id = ?",
                (lease, (note or "working")[:120], _iso(now), job_id),
            )
        return {"id": job_id, "status": "claimed", "lease_expires_at": lease}

    def complete(self, seat: dict[str, Any], job_id: str, token: str, content: str) -> dict[str, Any]:
        """Post exactly one reply and mark the job done, in one transaction.
        Repeating the call with the same claim returns the same reply."""
        content = _text(content, "content", MAX_MESSAGE_CHARS)
        with self._tx() as connection:
            row = connection.execute(
                "SELECT * FROM roundtable_jobs WHERE id = ? AND seat_id = ?", (job_id, seat["id"])
            ).fetchone()
            if (
                row is not None
                and row["status"] == "done"
                and row["claim_hash"]
                and hmac.compare_digest(row["claim_hash"], _hash(token or ""))
            ):
                reply = connection.execute(
                    "SELECT * FROM roundtable_messages WHERE id = ?", (row["reply_message_id"],)
                ).fetchone()
                return {"job": {"id": job_id, "status": "done"}, "message": dict(reply)}
            row = self._claimed_job(connection, seat, job_id, token)
            message = self._insert_message(
                connection, row["room_id"], "agent", seat["id"], seat["display_name"], content, row["trigger_message_id"]
            )
            connection.execute(
                "UPDATE roundtable_jobs SET status = 'done', reply_message_id = ?, note = NULL, updated_at = ? WHERE id = ?",
                (message["id"], _iso(_now()), job_id),
            )
        return {"job": {"id": job_id, "status": "done"}, "message": message}

    def fail(self, seat: dict[str, Any], job_id: str, token: str, error: str, retry: bool) -> dict[str, Any]:
        with self._tx() as connection:
            row = self._claimed_job(connection, seat, job_id, token)
            again = retry and row["attempts"] < MAX_ATTEMPTS
            new_status = "pending" if again else "failed"
            connection.execute(
                """
                UPDATE roundtable_jobs SET status = ?, reason = ?, claim_hash = NULL, note = NULL, updated_at = ?
                WHERE id = ?
                """,
                (new_status, (error or "failed")[:200], _iso(_now()), job_id),
            )
            if not again:
                self._insert_message(
                    connection,
                    row["room_id"],
                    "system",
                    None,
                    "Roundtable",
                    f"{seat['display_name']} could not answer ({(error or 'failed')[:120]}).",
                    row["trigger_message_id"],
                )
        return {"id": job_id, "status": new_status}
