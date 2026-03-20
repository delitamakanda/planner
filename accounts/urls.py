from rest_framework.routers import DefaultRouter
from django.urls import include, path

from accounts.viewsets import (
    UserViewSet,
    TeamViewSet,
    TeamMembershipViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'team-memberships', TeamMembershipViewSet, basename='team-membership'  )

urlpatterns = [
    path('', include(router.urls)),
]