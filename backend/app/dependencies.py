from fastapi import Request

from app.geoapify import GeoapifyClient
from app.groq import GroqClient


def get_geoapify_client(request: Request) -> GeoapifyClient:
    return request.app.state.geoapify


def get_groq_client(request: Request) -> GroqClient:
    return request.app.state.groq
