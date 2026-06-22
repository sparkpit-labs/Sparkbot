from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES
from app.main import app


def _category_by_id(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {category["id"]: category for category in payload["sensitive_action_categories"]}


def test_guardian_status_is_static_preview() -> None:
    client = TestClient(app)
    response = client.get("/guardian/status")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "sparkbot-server"
    assert payload["mode"] == "local"
    assert payload["status"] == "preview"
    assert payload["runtime_enforcement"] == "not-implemented"
    assert payload["approval_tokens"] == "not-implemented"
    assert payload["policy_decisions"] == "not-implemented"
    assert payload["audit_trail"] == "planned"
    assert payload["default_posture"] == "deny-sensitive-actions"
    assert payload["provider_execution_boundary"] == {
        "id": "lima-guardian-provider-runtime",
        "label": "LIMA Guardian provider runtime boundary",
        "status": "guarded-future",
        "runtime_gate": "lima-guardian-required",
        "dispatch": "fail-closed",
        "required_controls": [
            "capability-check",
            "operator-approval",
            "audit-log",
            "secret-redaction",
            "timeout",
            "no-shell-expansion",
        ],
        "blocked_until": "Codex and Claude subscription CLI dispatch requires a LIMA Guardian execution adapter.",
        "notes": "Sparkbot may report subscription sign-in readiness, but direct Codex or Claude CLI execution remains disabled until LIMA provides guarded dispatch with audit and fail-closed behavior.",
    }
    assert payload["sensitive_action_categories"] == [
        {
            "id": "external-sends",
            "label": "External sends",
            "status": "guarded-future",
            "notes": "No external sends are implemented.",
        },
        {
            "id": "connector-calls",
            "label": "Connector calls",
            "status": "guarded-future",
            "notes": "No connector calls are implemented.",
        },
        {
            "id": "credential-use",
            "label": "Credential use",
            "status": "guarded-future",
            "notes": "No credential use or storage is implemented.",
        },
        {
            "id": "model-provider-calls",
            "label": "Model provider calls",
            "status": "guarded-future",
            "notes": "No model provider calls are implemented.",
        },
        {
            "id": "file-writes",
            "label": "File writes",
            "status": "guarded-future",
            "notes": "No file mutation workflow is implemented.",
        },
        {
            "id": "tool-execution",
            "label": "Tool execution",
            "status": "guarded-future",
            "notes": "No terminal or tool execution is implemented.",
        },
    ]


def test_sensitive_action_categories_remain_guarded_future() -> None:
    client = TestClient(app)
    payload = client.get("/guardian/status").json()
    categories = _category_by_id(payload)

    assert {category["status"] for category in payload["sensitive_action_categories"]} <= ALLOWED_CAPABILITY_STATUSES
    assert all(category["status"] == "guarded-future" for category in payload["sensitive_action_categories"])
    assert all(category["status"] != "available" for category in payload["sensitive_action_categories"])
    assert categories["external-sends"]["status"] == "guarded-future"
    assert categories["connector-calls"]["status"] == "guarded-future"
    assert categories["credential-use"]["status"] == "guarded-future"
    assert categories["model-provider-calls"]["status"] == "guarded-future"
    assert categories["file-writes"]["status"] == "guarded-future"
    assert categories["tool-execution"]["status"] == "guarded-future"


def test_guardian_status_does_not_claim_active_runtime() -> None:
    client = TestClient(app)
    payload = client.get("/guardian/status").json()

    assert payload["runtime_enforcement"] == "not-implemented"
    assert payload["approval_tokens"] == "not-implemented"
    assert payload["policy_decisions"] == "not-implemented"
    assert payload["audit_trail"] == "planned"
    assert payload["default_posture"] == "deny-sensitive-actions"
    assert payload["provider_execution_boundary"]["status"] == "guarded-future"
    assert payload["provider_execution_boundary"]["dispatch"] == "fail-closed"
    assert payload["provider_execution_boundary"]["runtime_gate"] == "lima-guardian-required"
    assert "audit-log" in payload["provider_execution_boundary"]["required_controls"]
    assert "no-shell-expansion" in payload["provider_execution_boundary"]["required_controls"]

    serialized = str(payload).lower()
    assert "available" not in serialized
    assert "implemented policy engine" not in serialized
    assert "active enforcement" not in serialized
    assert "execution enabled" not in serialized


def test_no_guardian_runtime_endpoint_was_introduced() -> None:
    client = TestClient(app)

    for method_name in ["post", "put", "patch", "delete"]:
        method = getattr(client, method_name)
        response = method("/guardian/status")
        assert response.status_code == 405

    assert client.get("/guardian/approve").status_code == 404
    assert client.get("/guardian/execute").status_code == 404
    assert client.get("/guardian/decision").status_code == 404
    assert client.get("/guardian/policy/decision").status_code == 404
    assert client.post("/provider-config/codex-subscription/prompt", json={}).status_code == 404
    assert client.post("/provider-config/claude-subscription/prompt", json={}).status_code == 404
