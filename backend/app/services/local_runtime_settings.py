from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.services import local_model_adapter
from app.services.local_workstation_store import LocalWorkstationStore


def get_local_runtime_settings() -> dict[str, Any]:
    store = LocalWorkstationStore()
    local_model_status = local_model_adapter.get_ollama_status()
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "available",
        "configuration": "env-driven",
        "settings_writes": "not-supported",
        "credentials": "not-supported",
        "data_directory": {
            "configured_by": "SPARKBOT_DATA_DIR" if _data_dir_is_env_configured() else "default-user-data-dir",
            "display_path": _display_path(store.data_dir),
        },
        "sqlite_database": {
            "filename": store.database_path.name,
            "display_path": _display_path(store.database_path),
        },
        "local_models": {
            "enabled": local_model_status["local_models_enabled"],
            "status": local_model_status["status"],
            "adapter": local_model_status["adapter"],
            "base_url": local_model_status["base_url"],
            "base_url_policy": local_model_status["base_url_policy"],
            "configured_model": local_model_status["configured_model"],
            "prompt_calls": local_model_status["prompt_calls"],
            "credentials": local_model_status["credentials"],
            "configuration_error": local_model_status.get("configuration_error"),
        },
    }


def _data_dir_is_env_configured() -> bool:
    return bool(os.environ.get("SPARKBOT_DATA_DIR", "").strip())


def _display_path(path: Path) -> str:
    resolved = path.expanduser()
    try:
        relative = resolved.relative_to(Path.home())
    except ValueError:
        return str(resolved)
    if not relative.parts:
        return "~"
    return str(Path("~") / relative)
