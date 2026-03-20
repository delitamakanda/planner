from rest_framework import  viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.throttling import ScopedRateThrottle

from planning.models import Assignment
from planning.serializers import AssignmentSerializer
from api.filters import AssignmentFilter
from api.querysets import scope_to_user_teams
from accounts.permissions import IsAdminOrHr
from planning.services import PlanningService

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AssignmentFilter
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    
    def get_queryset(self):
        qs = (
            Assignment.objects.select_related('user', 'project', 'project_task', 'created_by')
            .all()
            .order_by('date_start')
        )
        return scope_to_user_teams(qs, self.request.user, user_field="user")
    
    def perform_create(self, serializer):
        return PlanningService.create_assignment(data=serializer.validated_data, user=self.request.user)
        
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrHr()]
        return super().get_permissions()
    
    def perform_update(self, serializer):
        return PlanningService.update_assignment(assignment=serializer.instance, data=serializer.validated_data)
    
    def get_throttles(self):
        if self.action in ['create', 'update', 'partial_update', "destroy"]:
            self.throttle_scope = 'planning_write'
        return super().get_throttles()
