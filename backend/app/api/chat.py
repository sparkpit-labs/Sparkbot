from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.settings import settings
from app.providers import ChatProviderError, ChatProviderRouter

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    provider: str | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    provider: str
    model: str
    content: str


def get_provider_router() -> ChatProviderRouter:
    return ChatProviderRouter(settings)


@router.get("/api/providers/status")
def provider_status(provider_router: ChatProviderRouter = Depends(get_provider_router)):
    try:
        return provider_router.status()
    except ChatProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, provider_router: ChatProviderRouter = Depends(get_provider_router)) -> ChatResponse:
    try:
        result = await provider_router.complete(
            message=request.message,
            provider=request.provider,
            model=request.model,
        )
    except ChatProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return ChatResponse(provider=result.provider, model=result.model, content=result.content)
