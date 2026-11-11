"""The standalone connector (tools/sparkbot-roundtable.py) against the real API.

No network, no model, no agent sign-in: HTTP goes through FastAPI's TestClient,
and agents are fakes (a Python object, or a fake ``claude`` executable).
"""

import importlib.util
import io
import json
import os
import stat
import sys
import textwrap
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("sparkbot_roundtable", ROOT / "tools" / "sparkbot-roundtable.py")
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)

BASE = "http://127.0.0.1:8000"
OWNER = {"X-Sparkbot-Local": "1"}


@pytest.fixture()
def api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SPARKBOT_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ROUNDTABLE_HOME", str(tmp_path / "profiles"))
    for name in ("SPARKBOT_URL", "SPARKBOT_SEAT_KEY", "ROUNDTABLE_PROFILE"):
        monkeypatch.delenv(name, raising=False)
    client = TestClient(app, base_url=BASE)

    def transport(method, url, body, headers):
        assert url.startswith(BASE)
        path = url[len(BASE):].replace("wait=25", "wait=0")  # no 25 s long-polls in tests
        response = client.request(method, path, json=body, headers=headers)
        return response.status_code, (response.json() if response.content else None)

    monkeypatch.setattr(rt, "urllib_transport", transport)
    return client


def owner_room(api: TestClient, name: str = "Planning") -> dict:
    return api.post("/roundtable/rooms", json={"name": name}, headers=OWNER).json()


def owner_say(api: TestClient, room_id: str, content: str) -> dict:
    return api.post(f"/roundtable/rooms/{room_id}/messages", json={"content": content}, headers=OWNER).json()


def replies_to(api: TestClient, room_id: str, message_id: str) -> list[tuple[str, str]]:
    msgs = api.get(f"/roundtable/rooms/{room_id}/messages", headers=OWNER).json()["messages"]
    return [(m["sender_name"], m["content"]) for m in msgs if m["reply_to_id"] == message_id and m["sender_kind"] == "agent"]


class FakeAgent:
    prompts: list[str] = []

    def __init__(self, timeout: float = 120, gate: threading.Event | None = None):
        self.gate = gate

    def run(self, prompt, checkpoint):
        FakeAgent.prompts.append(prompt)
        if self.gate is not None:
            while not self.gate.is_set():
                checkpoint()
                time.sleep(0.05)
            checkpoint()
        return "Fake agent here. I saw " + ("the question" if "what's next" in prompt else "nothing") + "."


def test_invite_saves_a_private_profile_and_whoami_works(api: TestClient, capsys) -> None:
    assert rt.main(["invite", "--room", "Planning", "--name", "Claude", "--slug", "claude"]) == 0
    profile = rt.config_path("claude")
    saved = json.loads(profile.read_text())
    assert saved["url"] == BASE and saved["key"].startswith("rts_")
    if os.name != "nt":
        assert stat.S_IMODE(profile.stat().st_mode) == 0o600
    assert rt.main(["whoami", "--profile", "claude"]) == 0
    assert "Claude (@claude) in room Planning" in capsys.readouterr().out
    # Invite again reuses the room by name.
    assert rt.main(["invite", "--room", "planning", "--name", "Codex", "--slug", "codex"]) == 0
    assert len(api.get("/roundtable/rooms", headers=OWNER).json()["rooms"]) == 1


def test_login_with_a_key_from_the_app(api: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    room = owner_room(api)
    seat = api.post(f"/roundtable/rooms/{room['id']}/seats", json={"display_name": "Codex", "slug": "codex"}, headers=OWNER).json()
    monkeypatch.setattr(rt, "read_seat_key", lambda: seat["key"])
    assert rt.main(["login", "--profile", "codex"]) == 0
    assert json.loads(rt.config_path("codex").read_text())["key"] == seat["key"]
    monkeypatch.setattr(rt, "read_seat_key", lambda: "rts_wrong_key")
    assert rt.main(["login", "--profile", "other"]) == 1
    assert not rt.config_path("other").exists()


def test_runner_answers_a_mention_once_without_seeing_the_key(api: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    FakeAgent.prompts = []
    monkeypatch.setitem(rt.RUNNER_ADAPTERS, "fake", FakeAgent)
    assert rt.main(["invite", "--room", "Planning", "--name", "Claude", "--slug", "claude"]) == 0
    room = api.get("/roundtable/rooms", headers=OWNER).json()["rooms"][0]
    key = json.loads(rt.config_path("claude").read_text())["key"]

    question = owner_say(api, room["id"], "@claude what's next?")
    assert rt.main(["run", "--profile", "claude", "--agent", "fake", "--once"]) == 0
    assert replies_to(api, room["id"], question["id"]) == [("Claude", "Fake agent here. I saw the question.")]
    assert key not in FakeAgent.prompts[0] and "rts_" not in FakeAgent.prompts[0]
    assert "claim_token" not in FakeAgent.prompts[0]

    # Nothing pending: --once returns without running the agent again.
    assert rt.main(["run", "--profile", "claude", "--agent", "fake", "--once"]) == 0
    assert len(FakeAgent.prompts) == 1

    log = (rt._home() / "roundtable-claude-runner.log").read_text()
    assert "completed" in log and "what's next" not in log and key not in log


def test_pause_while_the_agent_works_posts_nothing(api: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    gate = threading.Event()
    monkeypatch.setitem(rt.RUNNER_ADAPTERS, "slow", lambda timeout: FakeAgent(timeout, gate))
    assert rt.main(["invite", "--room", "Planning", "--name", "Claude", "--slug", "claude"]) == 0
    room = api.get("/roundtable/rooms", headers=OWNER).json()["rooms"][0]
    question = owner_say(api, room["id"], "@claude what's next?")
    FakeAgent.prompts = []
    worker = threading.Thread(target=rt.main, args=(["run", "--profile", "claude", "--agent", "slow", "--once"],))
    worker.start()
    for _ in range(100):
        if FakeAgent.prompts:
            break
        time.sleep(0.05)
    owner_say(api, room["id"], "/pause")
    gate.set()
    worker.join(20)
    assert not worker.is_alive()
    assert replies_to(api, room["id"], question["id"]) == []


def test_read_post_and_mcp(api: TestClient, capsys) -> None:
    assert rt.main(["invite", "--room", "Planning", "--name", "Codex", "--slug", "codex"]) == 0
    room = api.get("/roundtable/rooms", headers=OWNER).json()["rooms"][0]
    owner_say(api, room["id"], "hello agents")
    assert rt.main(["read", "--profile", "codex"]) == 0
    assert "hello agents" in capsys.readouterr().out
    assert rt.main(["read", "--profile", "codex"]) == 0
    assert "(no new messages)" in capsys.readouterr().out
    assert rt.main(["post", "--profile", "codex", "On", "it"]) == 0

    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "roundtable_post", "arguments": {"content": "via MCP"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "roundtable_read", "arguments": {"only_new": False}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "nope", "arguments": {}}},
    ]
    stdin = io.BytesIO("\n".join(json.dumps(r) for r in requests).encode() + b"\n")
    stdout = io.BytesIO()
    rt.McpServer(lambda: rt.Session("codex")).serve(stdin, stdout)
    out = [json.loads(line) for line in stdout.getvalue().decode().splitlines()]
    assert [r["id"] for r in out] == [1, 2, 3, 4, 5]
    assert {t["name"] for t in out[1]["result"]["tools"]} == {"roundtable_whoami", "roundtable_read", "roundtable_post", "roundtable_wait"}
    assert "Posted as Codex" in out[2]["result"]["content"][0]["text"]
    text = out[3]["result"]["content"][0]["text"]
    assert "hello agents" in text and "On it" in text and "via MCP" in text and "(you)" in text
    assert out[4]["error"]["code"] == -32602
    # Agent posts never wake agents.
    assert api.get(f"/roundtable/rooms/{room['id']}/seats", headers=OWNER).json()["seats"][0]["pending_jobs"] == 0


# -- runner edge cases (fake client) ---------------------------------------------


def sample_job() -> dict:
    return {
        "id": "0123456789abcdef0123456789abcdef",
        "claim_token": "claim-secret",
        "room": {"id": "room", "name": "Planning"},
        "trigger": {"id": "m1", "sender_name": "Owner", "sender_type": "HUMAN", "content": "@claude hi"},
        "context": [],
        "attempt": 1,
        "limits": {"max_reply_chars": 8000},
    }


class FakeStore:
    def __init__(self, allowed: bool = True):
        self.allowed, self.events = allowed, []

    def reserve(self) -> bool:
        return self.allowed

    def audit(self, event: str, job_id: str = "", reason: str = "") -> None:
        self.events.append(event)


class FakeClient:
    def __init__(self, fail_complete: list[Exception] | None = None, refuse: int | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.fail_complete = fail_complete or []
        self.refuse = refuse

    def job_action(self, job, action, **fields):
        self.calls.append((action, fields))
        if self.refuse and action == "heartbeat":
            raise rt.RoundtableError("refused", self.refuse)
        if action == "complete":
            if self.fail_complete:
                raise self.fail_complete.pop(0)
            return {"message": {"id": "reply"}}
        return {"job": {}}


class CountingAgent:
    def __init__(self):
        self.runs = 0

    def run(self, prompt, checkpoint):
        self.runs += 1
        return "answer"


def test_lost_ack_retries_the_same_completion_without_rerunning() -> None:
    client, agent = FakeClient([rt.RoundtableError("down", 503)]), CountingAgent()
    rt.Runner(client, agent, FakeStore(), "Claude", sleep=lambda s: None).process(sample_job())
    completes = [fields for action, fields in client.calls if action == "complete"]
    assert agent.runs == 1 and len(completes) == 2 and completes[0] == completes[1]


def test_cancelled_or_removed_seat_never_runs_the_agent() -> None:
    agent = CountingAgent()
    rt.Runner(FakeClient(refuse=409), agent, FakeStore(), "Claude").process(sample_job())
    assert agent.runs == 0
    with pytest.raises(rt.RoundtableError, match="refused"):
        rt.Runner(FakeClient(refuse=401), agent, FakeStore(), "Claude").process(sample_job())
    assert agent.runs == 0


def test_local_cap_fails_the_job_without_running_the_agent() -> None:
    client, agent = FakeClient(), CountingAgent()
    rt.Runner(client, agent, FakeStore(allowed=False), "Claude").process(sample_job())
    assert agent.runs == 0 and client.calls[-1][0] == "fail"


def test_quota_survives_restart_and_one_runner_per_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROUNDTABLE_HOME", str(tmp_path))
    with rt.RunnerStore("claude", hourly_cap=2) as store:
        assert store.reserve(1000) and store.reserve(1001)
        with pytest.raises(rt.RoundtableError, match="already using"):
            rt.RunnerStore("claude").__enter__()
    with rt.RunnerStore("claude", hourly_cap=2) as store:
        assert not store.reserve(1002)
        assert store.reserve(1000 + 3601)


def test_prompt_keeps_the_trigger_and_drops_old_context() -> None:
    job = sample_job()
    job["context"] = [{"sender_name": "x", "content": "y" * 4000} for _ in range(30)]
    prompt = rt.runner_prompt(job, "Claude")
    assert "@claude hi" in prompt and len(prompt.encode()) < 70000
    assert "claim-secret" not in prompt


def test_agent_environment_has_no_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("SPARKBOT_SEAT_KEY", "rts_x_y")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", "/somewhere")
    env = rt.runner_environment()
    assert not {"ANTHROPIC_API_KEY", "OPENAI_API_KEY", "SPARKBOT_SEAT_KEY"} & set(env)
    assert env["CLAUDE_CONFIG_DIR"] == "/somewhere"


def test_codex_command_is_isolated() -> None:
    command = rt.codex_command("codex", "/tmp/w", "/tmp/w/out.txt")
    joined = " ".join(command)
    for part in ("--ignore-user-config", "--ephemeral", "--sandbox read-only", "mcp_servers={}", 'web_search="disabled"', "--disable shell_tool"):
        assert part in joined
    assert command[-1] == "-"


def test_windows_npm_shims_resolve_to_native_binaries(tmp_path: Path) -> None:
    shim = tmp_path / "claude.cmd"
    shim.write_text("@echo off")
    native = tmp_path / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
    native.parent.mkdir(parents=True)
    native.write_bytes(b"MZ")
    with patch.object(rt.shutil, "which", return_value=str(shim)):
        assert rt.claude_executable() == str(native)
    with patch.object(rt.shutil, "which", return_value=None):
        with pytest.raises(rt.RoundtableError):
            rt.claude_executable()
        with pytest.raises(rt.RoundtableError):
            rt.codex_executable()


# -- Claude adapter with a fake executable -------------------------------------

FAKE_CLAUDE = textwrap.dedent(
    """\
    #!{python}
    import json, os, sys, time
    if sys.argv[1:] == ["--help"]:
        print("--tools --strict-mcp-config --mcp-config --setting-sources --disable-slash-commands --no-session-persistence" if "{mode}" != "old" else "--print")
        sys.exit(0)
    prompt = sys.stdin.read()
    json.dump({{"argv": sys.argv[1:], "env": sorted(os.environ), "cwd": os.getcwd(),
               "mcp": open(sys.argv[sys.argv.index("--mcp-config") + 1]).read()}}, open("{record}", "w"))
    if "{mode}" == "sleep":
        time.sleep(30)
    if "{mode}" == "signedout":
        print("Failed to authenticate: session expired")
        sys.exit(1)
    print("Claude here, " + str(len(prompt)) + " chars read.")
    """
)


@pytest.mark.skipif(os.name == "nt", reason="fake executable uses a POSIX shebang")
@pytest.mark.parametrize("mode", ["ok", "old", "sleep", "signedout"])
def test_claude_adapter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    record = tmp_path / "record.json"
    exe = tmp_path / "claude"
    exe.write_text(FAKE_CLAUDE.format(python=sys.executable, record=record, mode=mode))
    exe.chmod(0o755)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "should-not-leak")
    monkeypatch.setattr(rt, "claude_executable", lambda: str(exe))
    adapter = rt.ClaudeAdapter(timeout=1 if mode == "sleep" else 20)
    prompt = rt.runner_prompt(sample_job(), "Claude")
    if mode == "old":
        with pytest.raises(rt.RoundtableError, match="isolation flags"):
            adapter.run(prompt, lambda: None)
        return
    if mode == "sleep":
        start = time.monotonic()
        with pytest.raises(rt.RoundtableError, match="timeout"):
            adapter.run(prompt, lambda: None)
        assert time.monotonic() - start < 15
        return
    if mode == "signedout":
        with pytest.raises(rt.RoundtableError, match="signed out"):
            adapter.run(prompt, lambda: None)
        return
    assert adapter.run(prompt, lambda: None).startswith("Claude here")
    seen = json.loads(record.read_text())
    argv = seen["argv"]
    assert argv[argv.index("--tools") + 1] == ""
    assert argv[argv.index("--setting-sources") + 1] == "local"
    assert json.loads(seen["mcp"]) == {"mcpServers": {}}
    assert "--bare" not in argv and all("ROOM DATA" not in a for a in argv)
    assert "ANTHROPIC_API_KEY" not in seen["env"]
    assert "roundtable-run-" in seen["cwd"] and not Path(seen["cwd"]).exists()


def test_missing_cli_fails_before_listening(api, monkeypatch, capsys):
    rt.main(["invite", "--name", "Claude", "--slug", "claude"])
    monkeypatch.setattr(rt, "claude_executable", lambda: (_ for _ in ()).throw(rt.RoundtableError("Claude Code CLI not found. Install it and sign in first.")))
    assert rt.main(["run", "--profile", "claude", "--agent", "claude", "--once"]) == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err
    assert "is listening" not in captured.out


def test_claude_native_install_without_path(monkeypatch, tmp_path):
    monkeypatch.setattr(rt.shutil, "which", lambda _: None)
    monkeypatch.setattr(rt.Path, "home", lambda: tmp_path)
    binary = tmp_path / ".local" / "bin" / ("claude.exe" if os.name == "nt" else "claude")
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"fake")
    assert rt.claude_executable() == str(binary)


def test_failed_job_is_visible_without_logging_secret(api, monkeypatch, capsys):
    class Broken(FakeAgent):
        def run(self, prompt, checkpoint):
            raise rt.RoundtableError("Claude Code CLI not found. Install it and sign in first.")
    monkeypatch.setitem(rt.RUNNER_ADAPTERS, "fake", Broken)
    rt.main(["invite", "--name", "Claude", "--slug", "claude"])
    room = api.get("/roundtable/rooms", headers=OWNER).json()["rooms"][0]
    owner_say(api, room["id"], "@claude hello")
    rt.main(["run", "--profile", "claude", "--agent", "fake", "--once"])
    assert "not found" in capsys.readouterr().err
    log = (rt._home() / "roundtable-claude-runner.log").read_text()
    assert "CLI not found" in log and "rts_" not in log
    result = api.get(f"/roundtable/rooms/{room['id']}", headers=OWNER).json()
    assert result["jobs"][0]["status"] == "failed"
    assert "CLI not found" in result["jobs"][0]["reason"]
    assert "claim_hash" not in json.dumps(result["jobs"])
    assert api.get(f"/roundtable/rooms/{room['id']}").status_code == 403
    assert rt.safe_failure_reason("secret rts_example") == "Agent or connection failed; check the CLI login and connection, then send a new mention."


@pytest.mark.parametrize("characters,expected", [(list("sample\r"), "sample"), (list("ab\bc\r"), "ac")])
def test_windows_hidden_key_input(characters, expected):
    class Keyboard:
        def kbhit(self): return bool(characters)
        def getwch(self): return characters.pop(0)
    assert rt._windows_key_loop(Keyboard(), lambda: True) == expected


def test_windows_login_timeout_closed_console_and_cancel():
    class Keyboard:
        def kbhit(self): return False
    now = [0.0]
    def advance(seconds): now[0] += seconds
    with pytest.raises(rt.RoundtableError, match="timed out"):
        rt._windows_key_loop(Keyboard(), lambda: True, timeout=0.1, clock=lambda: now[0], sleep=advance)
    with pytest.raises(rt.RoundtableError, match="terminal closed"):
        rt._windows_key_loop(Keyboard(), lambda: False)
    class Cancel:
        def kbhit(self): return True
        def getwch(self): return "\x1b"
    with pytest.raises(rt.RoundtableError, match="cancelled"):
        rt._windows_key_loop(Cancel(), lambda: True)
