from fastapi import APIRouter, Depends

from app.dependencies import get_geoapify_client, get_groq_client
from app.geoapify import GeoapifyClient
from app.groq import GroqClient
from app.schemas import ChatRequest, ChatResponse
from app.services import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post(
    "/assistant",
    response_model=ChatResponse,
    summary="Asistente turístico de Manizales (grounding solo con Geoapify)",
)
async def assistant_chat(
    body: ChatRequest,
    client: GeoapifyClient = Depends(get_geoapify_client),
    groq_client: GroqClient = Depends(get_groq_client),
) -> ChatResponse:
    service = ChatService(client, groq_client)
    result = await service.ask(
        question=body.question,
        category=body.category,
        latitude=body.latitude,
        longitude=body.longitude,
        radius_m=body.radius_m,
        limit=body.limit,
    )
    return ChatResponse(**result)
