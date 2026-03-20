from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from projects.models import Project, Client, ProjectTask
from projects.serializers import ClientSerializer, ProjectTaskSerializer, ProjectSerializer
from api.filters import ProjectFilter
from accounts.permissions import IsAuthenticatedAndReadOnly, IsAdminOrHr, is_admin, is_hr, manages_team_ids

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('name')
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticatedAndReadOnly,]
    

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter
    
    def get_queryset(self):
        qs = (
            Project.objects.select_related('client', 'owner')
            .prefetch_related("teams")
            .all()
            .order_by('-updated_at')
        )
        u = self.request.user
        if is_admin(u) or is_hr(u):
            return qs
        team_ids = manages_team_ids(u)
        if team_ids:
            return qs.filter(teams__id__in=team_ids).distinct()
        return qs.filter(teams_memberships__user=u).distinct()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrHr()]
        return super().get_permissions()
    
class ProjectTaskViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs = ProjectTask.objects.select_related('project', 'parent').all().order_by('id')
        u = self.request.user
        if is_admin(u) or is_hr(u):
            return qs
        team_ids = manages_team_ids(u)
        if team_ids:
            return qs.filter(project__teams__id__in=team_ids).distinct()
        return qs.filter(project__teams_memberships__user=u).distinct()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrHr()]
        return super().get_permissions()
