from rest_framework.routers import DefaultRouter
from django.urls import include, path
from leaves.viewsets import (
    LeaveTypeViewSet,
    LeaveBalanceViewSet,
    LeaveRequestViewSet,
)

router = DefaultRouter()
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leave-balance')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')

urlpatterns = [
    path('', include(router.urls)),
]