from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import time

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "OK", "timestamp": int(time.time() * 1000)})


@api_view(['GET'])
@permission_classes([AllowAny])
def schema_check(request):
    t0 = time.time()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return Response({"status": "OK", "db_ms": int((time.time() - t0) * 1000)})