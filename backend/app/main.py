from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.settings import settings

app = FastAPI(title=settings.project_name)
app.include_router(health_router)

