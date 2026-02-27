from django.urls import path
from api.health import health_check, schema_check

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('check/', schema_check, name='schema_check'),
]