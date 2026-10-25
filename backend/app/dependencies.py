from fastapi import Request

from app.groq import GroqClient
from app.places_source import PlaceSource


def get_place_source(request: Request) -> PlaceSource:
    return request.app.state.place_source


def get_groq_client(request: Request) -> GroqClient:
    return request.app.state.groq
