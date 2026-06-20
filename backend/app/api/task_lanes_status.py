from typing import Literal, TypedDict

from fastapi import APIRouter

from app.api.capabilities import ALLOWED_CAPABILITY_STATUSES, CapabilityStatus

router = APIRouter()

ImplementationStatus = Literal["not-implemented"]


class TaskLane(TypedDict):
    id: str
    label: str
    status: CapabilityStatus
    notes: str


class TaskLanesStatusResponse(TypedDict):
    service: str
    mode: str
    status: CapabilityStatus
    task_runtime: ImplementationStatus
    task_persistence: ImplementationStatus
    scheduler: ImplementationStatus
    background_jobs: ImplementationStatus
    notifications: ImplementationStatus
    lanes: list[TaskLane]


TASK_LANES: list[TaskLane] = [
    {
        "id": "inbox",
        "label": "Inbox Lane",
        "status": "preview",
        "notes": "Read-only lane preview. No tasks are stored or executed.",
    },
    {
        "id": "planned",
        "label": "Planned Lane",
        "status": "planned",
        "notes": "Future planning lane. No scheduler is implemented.",
    },
    {
        "id": "active",
        "label": "Active Lane",
        "status": "planned",
        "notes": "Future active work lane. No task runtime is implemented.",
    },
    {
        "id": "review",
        "label": "Review Lane",
        "status": "planned",
        "notes": "Future review lane. No workflow runtime is implemented.",
    },
]


@router.get("/work-lanes/status")
def task_lanes_status() -> TaskLanesStatusResponse:
    return {
        "service": "sparkbot-server",
        "mode": "local",
        "status": "preview",
        "task_runtime": "not-implemented",
        "task_persistence": "not-implemented",
        "scheduler": "not-implemented",
        "background_jobs": "not-implemented",
        "notifications": "not-implemented",
        "lanes": TASK_LANES,
    }


assert {lane["status"] for lane in TASK_LANES} <= ALLOWED_CAPABILITY_STATUSES
