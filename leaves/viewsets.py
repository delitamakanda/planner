from __future__ import annotations
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from leaves.models import LeaveType, LeaveBalance, LeaveRequest
from leaves.serializers import LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer
from api.filters import LeaveRequestFilter
from leaves.services import LeaveService
from leaves.permissions import LeaveRequestPermission, is_hr, is_admin, manages_team_ids
from api.querysets import scope_to_user_teams
from accounts.permissions import IsAdminOrHr, IsAuthenticatedAndReadOnly, is_admin, is_hr, manages_team_ids


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all().order_by('code')
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAdminOrHr,]
    
    
class LeaveBalanceViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        qs = LeaveBalance.objects.select_related('user', 'leave_type').all()
        return scope_to_user_teams(qs, self.request.user, user_field="user")
    
    
class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated,]
    filter_backends = [DjangoFilterBackend,]
    filterset_class = LeaveRequestFilter
    
    def get_queryset(self):
        qs = (
            LeaveRequest.objects.select_related('user', 'leave_type', 'manager_approver', 'hr_approver').all()
            .order_by('-created_at')
        )
        return scope_to_user_teams(qs, self.request.user, user_field="user")
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
    @action(detail=True, methods=['POST'])
    def submit(self, request, pk=None):
        lr: LeaveRequest = self.get_object()
        try:
            lr = LeaveService.submit(lr=lr, user=request.user)
        except PermissionError:
            return Response({"detail": "Forbidden"}, status=403)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response(self.get_serializer(lr).data)
    
    @action(detail=True, methods=['POST'])
    def approve(self, request, pk=None):
        lr: LeaveRequest = self.get_object()
        
        approved_as = "HR" if is_hr(request.user) else "manager"
        
        if is_admin(request.user):
            approved_as = "manager"
            
        try:
            lr = LeaveService.approve(lr=lr, user=request.user, approved_as=approved_as)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response(self.get_serializer(lr).data)
    
    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        lr: LeaveRequest = self.get_object()
        
        rejected_as = "HR" if is_hr(request.user) else "manager"
        if is_admin(request.user):
            rejected_as = "manager"
        
        try:
            lr = LeaveService.reject(lr=lr, user=request.user, rejected_as=rejected_as)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        
        return Response(self.get_serializer(lr).data)
    
    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        lr: LeaveRequest = self.get_object()
        try:
            lr = LeaveService.cancel(lr=lr, user=request.user)
        except PermissionError:
            return Response({"detail": "Forbidden"}, status=403)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response(self.get_serializer(lr).data)
