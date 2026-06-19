from fastapi import FastAPI

from app.api.capabilities import router as capabilities_router
from app.api.connector_status import router as connector_status_router
from app.api.guardian_status import router as guardian_status_router
from app.api.health import router as health_router
from app.api.provider_config import router as provider_config_router
from app.core.settings import settings

app = FastAPI(title=settings.project_name)
app.include_router(health_router)
app.include_router(capabilities_router)
app.include_router(connector_status_router)
app.include_router(guardian_status_router)
app.include_router(provider_config_router)

