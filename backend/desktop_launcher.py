"""Packaged loopback backend; its lifetime belongs to the desktop stdin pipe."""

from __future__ import annotations

import os
import sys
import threading

PORT = 18765


def main() -> None:
    # Packaged windows need these exact origins; do not enable wildcard CORS.
    os.environ["SPARKBOT_ALLOWED_ORIGINS"] = "http://tauri.localhost,https://tauri.localhost,tauri://localhost"
    os.environ.pop("SPARKBOT_ALLOWED_HOSTS", None)
    import uvicorn
    from app.main import app
    app.state.desktop_shutdown = threading.Event()

    class DesktopServer(uvicorn.Server):
        async def startup(self, sockets=None):
            await super().startup(sockets=sockets)
            if self.started:
                print("SPARKBOT_READY", flush=True)

    server = DesktopServer(uvicorn.Config(
        app, host="127.0.0.1", port=PORT, log_level="warning", access_log=False,
        timeout_graceful_shutdown=2,
    ))

    def watch_parent() -> None:
        sys.stdin.buffer.read()
        app.state.desktop_shutdown.set()
        server.should_exit = True

    threading.Thread(target=watch_parent, daemon=True).start()
    server.run()


if __name__ == "__main__":
    main()
