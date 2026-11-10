"""Exercise the packaged backend without opening a window or calling a model."""
from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def request(path, data=None, headers=None, method=None):
    req = Request("http://127.0.0.1:18765" + path,
                  data=json.dumps(data).encode() if data is not None else None,
                  headers={"Content-Type": "application/json", "X-Sparkbot-Local": "1", **(headers or {})},
                  method=method)
    with urlopen(req, timeout=10) as response:
        return json.load(response)


def start(command, env):
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    result = queue.Queue()
    threading.Thread(target=lambda: result.put(child.stdout.readline()), daemon=True).start()
    try:
        assert result.get(timeout=45).strip() == b"SPARKBOT_READY", "Backend did not become ready"
    except BaseException:
        stop(child)
        raise
    return child


def stop(child):
    if child.stdin and not child.stdin.closed:
        child.stdin.close()
    try:
        child.wait(timeout=10)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()
        raise AssertionError("Backend failed to exit after parent pipe closed")


def main():
    command = sys.argv[1:]
    assert command, "Pass backend executable or python desktop_launcher.py"
    with tempfile.TemporaryDirectory(prefix="sparkbot-desktop-smoke-") as temporary:
        env = {**os.environ, "SPARKBOT_DATA_DIR": temporary}
        child = start(command, env)
        try:
            assert request("/health")["status"] == "ok"
            room = request("/roundtable/rooms", {"name": "Desktop smoke"})
            room_id = room["id"]
            request(f"/roundtable/rooms/{room_id}/messages", {"content": "Synthetic desktop smoke message"})
            try:
                request("/roundtable/rooms", headers={"X-Sparkbot-Local": "0"})
                raise AssertionError("Owner header was not enforced")
            except HTTPError as error:
                assert error.code == 403
            preflight = Request("http://127.0.0.1:18765/roundtable/rooms", method="OPTIONS",
                                headers={"Origin": "http://tauri.localhost", "Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "X-Sparkbot-Local"})
            with urlopen(preflight, timeout=10) as response:
                assert response.headers["Access-Control-Allow-Origin"] == "http://tauri.localhost"
            # A second instance must fail, never attach to or stop the first.
            second = subprocess.run(command, input=b"", capture_output=True, env=env, timeout=45)
            assert second.returncode != 0 and b"SPARKBOT_READY" not in second.stdout
            assert request("/health")["status"] == "ok"
        finally:
            stop(child)
        child = start(command, env)
        try:
            saved = request(f"/roundtable/rooms/{room_id}")
            assert saved["name"] == "Desktop smoke"
        finally:
            stop(child)
    print("PASS: packaged backend startup, room write, owner guard, desktop CORS, port conflict, persistence and shutdown")


if __name__ == "__main__":
    main()
