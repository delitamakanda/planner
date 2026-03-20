from rest_framework.routers import DefaultRouter
from django.urls import include, path

from projects.viewsets import (
    ClientViewSet,
    ProjectViewSet,
    ProjectTaskViewSet,
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'project-tasks', ProjectTaskViewSet, basename='project-task')

urlpatterns = [
    path('', include(router.urls)),
]
