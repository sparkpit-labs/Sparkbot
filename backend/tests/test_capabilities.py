from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app


def _capability_by_id(payload: dict) -> dict[str, dict]:
    return {item["id"]: item for item in payload["capabilities"]}


def test_capabilities_are_static_and_public_safe() -> None:
    client = TestClient(app)
    response = client.get("/capabilities")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["capabilities"] == [
        {
            "id": "backend-health",
            "label": "Backend health endpoint",
            "status": "available",
            "notes": "Read-only local health check.",
        },
        {
            "id": "frontend-shell",
            "label": "Frontend shell",
            "status": "available",
            "notes": "Public shell interface.",
        },
        {
            "id": "workstation",
            "label": "Workstation shell",
            "status": "preview",
            "notes": "Navigation and product shell preview.",
        },
        {
            "id": "chat",
            "label": "Chat shell",
            "status": "preview",
            "notes": "No model calls or message persistence.",
        },
        {
            "id": "round-table",
            "label": "Round Table",
            "status": "preview",
            "notes": "No meeting engine or agent orchestration.",
        },
        {
            "id": "provider-setup",
            "label": "Provider Setup shell",
            "status": "preview",
            "notes": "No credential storage or provider calls.",
        },
        {
            "id": "guardian-controls",
            "label": "Guardian Controls shell",
            "status": "preview",
            "notes": "No policy enforcement runtime.",
        },
        {
            "id": "desktop-packaging",
            "label": "Desktop packaging",
            "status": "planned",
            "notes": "No installer or desktop binary yet.",
        },
        {
            "id": "connectors",
            "label": "Connectors",
            "status": "guarded-future",
            "notes": "No connector calls or external sends.",
        },
        {
            "id": "model-calls",
            "label": "Model calls",
            "status": "guarded-future",
            "notes": "No provider runtime or model routing.",
        },
        {
            "id": "credential-storage",
            "label": "Credential storage",
            "status": "guarded-future",
            "notes": "No credential entry or storage path.",
        },
        {
            "id": "tool-execution",
            "label": "Tool execution",
            "status": "guarded-future",
            "notes": "No terminal, tool, or automation execution.",
        },
    ]


def test_capability_statuses_use_contract_values() -> None:
    client = TestClient(app)
    payload = client.get("/capabilities").json()

    statuses = {item["status"] for item in payload["capabilities"]}
    assert statuses <= ALLOWED_CAPABILITY_STATUSES
    assert "disabled-by-default" in ALLOWED_CAPABILITY_STATUSES
    assert "guarded-future" in statuses


def test_guarded_future_capabilities_are_present_and_inactive() -> None:
    client = TestClient(app)
    payload = client.get("/capabilities").json()
    capabilities = _capability_by_id(payload)

    for capability_id in ["connectors", "model-calls", "credential-storage", "tool-execution"]:
        assert capabilities[capability_id]["status"] == "guarded-future"

    inactive_notes = " ".join(item["notes"].lower() for item in payload["capabilities"])
    assert "no connector calls" in inactive_notes
    assert "external sends" in inactive_notes
    assert "no provider runtime" in inactive_notes
    assert "no credential entry" in inactive_notes
    assert "no terminal" in inactive_notes
    assert "available" not in {
        capabilities["connectors"]["status"],
        capabilities["model-calls"]["status"],
        capabilities["credential-storage"]["status"],
        capabilities["tool-execution"]["status"],
    }
