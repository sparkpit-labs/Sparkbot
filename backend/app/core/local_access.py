"""Keep the local API local.

Sparkbot's backend binds to 127.0.0.1. Two extra guards:

* ``Host`` must be a loopback name, so a web page can't reach the API through
  DNS rebinding.
* Browsers may only call the API from the Sparkbot frontend's own origin
  (CORS). Owner routes also need a custom header, which forces that CORS check.
"""

from __future__ import annotations

import os

from fastapi import HTTPException, Request, status

DEFAULT_ALLOWED_HOSTS = ("127.0.0.1", "localhost", "::1")
DEFAULT_ALLOWED_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:15173",
    "http://localhost:15173",
)


def _env_list(name: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


def allowed_hosts() -> set[str]:
    return {*DEFAULT_ALLOWED_HOSTS, *_env_list("SPARKBOT_ALLOWED_HOSTS")}


def allowed_origins() -> list[str]:
    return [*DEFAULT_ALLOWED_ORIGINS, *_env_list("SPARKBOT_ALLOWED_ORIGINS")]


def request_hostname(request: Request) -> str:
    host = request.headers.get("host", "")
    if host.startswith("["):
        return host[1:].split("]", 1)[0]
    return host.rsplit(":", 1)[0] if host.count(":") == 1 else host


def require_local_host(request: Request) -> None:
    if request_hostname(request) not in allowed_hosts():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sparkbot's local API only answers on localhost")
