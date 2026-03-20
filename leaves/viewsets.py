from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from leaves.models import LeaveType, LeaveBalance, LeaveRequest
from leaves.serializers import LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer
from api.filters import LeaveRequestFilter
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
        u = self.request.user
        if is_admin(u) or is_hr(u):
            return qs
        team_ids = manages_team_ids(u)
        if team_ids:
            return qs.filter(user__team_memberships__team_id__in=team_ids).distinct()
        return qs.filter(user=u.id)
    
    
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
        
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticatedAndReadOnly]
        return super().get_permissions()
    
    @action(detail=True, methods=['POST'])
    def submit(self, request, pk=None):
        lr: LeaveRequest = self.get_object()
        if lr.user.id != request.user.id and not is_admin(request.user) and not is_hr(request.user):
            return Response({"detail": "Forbidden"}, status=403)
        
        if lr.status != LeaveRequest.Status.PENDING:
            return Response({"detail": "Invalid status"}, status=400)
        
        lr.status = LeaveRequest.Status.SUBMITTED
        lr.submitted_at = timezone.now()
        lr.save(update_fields=['status','submitted_at'])
        return Response(self.get_serializer(lr).data)
    
    @action(detail=True, methods=['POST'])
    def approve(self, request, pk=None):
        lr: LeaveRequest = self.get_object()
        u = request.user
        
        if not is_admin(u) and not is_hr(u):
            team_ids = manages_team_ids(u)
            if not team_ids:
                return Response({"detail": "Forbidden"}, status=403)
            if not lr.user.team_memberships.filter(team_id__in=team_ids).exists():
                return Response({"detail": "Forbidden"}, status=403)

        if lr.status != LeaveRequest.Status.SUBMITTED:
            return Response({"detail": "Invalid status"}, status=400)
        lr.status = LeaveRequest.Status.APPROVED
        lr.decided_at = timezone.now()
        
        if is_hr(u):
            lr.hr_approver = u
        else:
            lr.manager_approver = u
        lr.save(update_fields=['status', 'decided_at', 'hr_approver','manager_approver'])
        return Response(self.get_serializer(lr).data)
    
    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        lr: LeaveRequest = self.get_object()
        u = request.user
        
        if not is_admin(u) or not is_hr(u) or manages_team_ids(u):
            return Response({"detail": "Forbidden"}, status=403)
        
        if lr.status != LeaveRequest.Status.SUBMITTED:
            return Response({"detail": "Invalid status"}, status=400)
        
        lr.status = LeaveRequest.Status.REJECTED
        lr.decided_at = timezone.now()
        if is_hr(u):
            lr.hr_approver = u
        else:
            lr.manager_approver = u
        lr.save(update_fields=['status', 'decided_at', 'hr_approver','manager_approver'])
        return Response(self.get_serializer(lr).data)
