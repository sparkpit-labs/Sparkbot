from fastapi.testclient import TestClient

from app.main import app


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
            "status": "available",
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
            "label": "Provider Setup",
            "status": "preview",
            "notes": "No credential storage or provider calls.",
        },
        {
            "id": "guardian-controls",
            "label": "Guardian Controls",
            "status": "preview",
            "notes": "No policy enforcement runtime.",
        },
        {
            "id": "desktop-packaging",
            "label": "Desktop packaging",
            "status": "planned",
            "notes": "No installer or desktop binary yet.",
        },
    ]
