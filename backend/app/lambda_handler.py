"""Punto de entrada para AWS Lambda.

Mangum traduce el evento que envía la Function URL de Lambda (formato HTTP API v2)
a una petición ASGI que FastAPI entiende, y convierte la respuesta de vuelta.
En Lambda se configura el handler como: app.lambda_handler.handler
"""
from mangum import Mangum

from app.main import app

handler = Mangum(app, lifespan="auto")
