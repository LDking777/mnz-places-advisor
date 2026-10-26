"""Verifica que el adaptador de Lambda responde a un evento de Function URL."""
import asyncio
import json

from app.lambda_handler import handler


def _function_url_event(path: str) -> dict:
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": "",
        "headers": {"host": "ejemplo.lambda-url.us-east-1.on.aws", "accept": "application/json"},
        "requestContext": {
            "accountId": "anonymous",
            "apiId": "ejemplo",
            "domainName": "ejemplo.lambda-url.us-east-1.on.aws",
            "domainPrefix": "ejemplo",
            "http": {
                "method": "GET",
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest",
            },
            "requestId": "id",
            "routeKey": "$default",
            "stage": "$default",
            "time": "01/Jan/2026:00:00:00 +0000",
            "timeEpoch": 0,
        },
        "isBase64Encoded": False,
    }


def test_health_via_lambda_event():
    # Lambda ejecuta el handler en un proceso nuevo con su propio event loop; aquí lo simulamos
    asyncio.set_event_loop(asyncio.new_event_loop())
    response = handler(_function_url_event("/health"), None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"status": "ok"}
