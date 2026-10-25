from fastapi import APIRouter, Depends

from app.dependencies import get_groq_client, get_place_source
from app.groq import GroqClient
from app.places_source import PlaceSource
from app.schemas import ChatRequest, ChatResponse
from app.services import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post(
    "/assistant",
    response_model=ChatResponse,
    summary="Asistente turístico de Manizales (grounding con la fuente de lugares)",
)
async def assistant_chat(
    body: ChatRequest,
    place_source: PlaceSource = Depends(get_place_source),
    groq_client: GroqClient = Depends(get_groq_client),
) -> ChatResponse:
    service = ChatService(place_source, groq_client)
    result = await service.ask(
        question=body.question,
        category=body.category,
        latitude=body.latitude,
        longitude=body.longitude,
        radius_m=body.radius_m,
        limit=body.limit,
    )
    return ChatResponse(**result)
