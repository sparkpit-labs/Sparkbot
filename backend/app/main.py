from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.capabilities import router as capabilities_router
from app.api.chat_status import router as chat_status_router
from app.api.command_center import router as command_center_router
from app.api.connector_status import router as connector_status_router
from app.api.guardian_status import router as guardian_status_router
from app.api.health import router as health_router
from app.api.local_models import router as local_models_router
from app.api.local_workstation import router as local_workstation_router
from app.api.model_seats_status import router as model_seats_status_router
from app.api.provider_config import router as provider_config_router
from app.api.round_table_status import router as round_table_status_router
from app.api.roundtable import router as roundtable_router
from app.api.task_lanes_status import router as task_lanes_status_router
from app.core.local_access import allowed_origins
from app.core.settings import settings

app = FastAPI(title=settings.project_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Sparkbot-Local"],
)
app.include_router(health_router)
app.include_router(local_workstation_router)
app.include_router(local_models_router)
app.include_router(capabilities_router)
app.include_router(chat_status_router)
app.include_router(connector_status_router)
app.include_router(guardian_status_router)
app.include_router(model_seats_status_router)
app.include_router(provider_config_router)
app.include_router(round_table_status_router)
app.include_router(roundtable_router)
app.include_router(task_lanes_status_router)
app.include_router(command_center_router)
