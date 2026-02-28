from __future__ import annotations
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import uuid

def custom_exception_handler(exc, context):
    request = context.get('request')
    rid = request.headers.get('X-Request-Id') if request else None
    request_id = rid or str(uuid.uuid4())
    
    response = drf_exception_handler(exc, context)
    if response is None:
        return Response(
            {
                "error": {
                    "code": "internal_error",
                    "message": "Internal Server Error",
                    "details": None,
                },
                "meta": {
                    "request_id": request_id,
                    "timestamp": timezone.now().isoformat(),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response(
        {
            "error": {
                "code": getattr(exc, "code", "unknown_error"),
                "message": str(exc),
                "details": response.data,
            },
            "meta": {
                "request_id": request_id,
                "timestamp": timezone.now().isoformat(),
            }
        },
        status=response.status_code,
        headers=response.headers
    )