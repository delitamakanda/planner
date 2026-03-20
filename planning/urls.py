from rest_framework.routers import DefaultRouter
from django.urls import include, path

from planning.viewsets import AssignmentViewSet

router = DefaultRouter()
router.register(r'assignments', AssignmentViewSet, basename='assignment')

urlpatterns = [
    path('', include(router.urls)),
]