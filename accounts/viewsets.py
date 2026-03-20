from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.models import User, TeamMembership, Team
from accounts.serializers import UserSerializer, TeamSerializer, TeamMembershipSerializer
from accounts.permissions import IsAdmin, IsAuthenticatedAndReadOnly, manages_team_ids, IsAdminOrHr, is_admin, is_hr

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        qs = User.objects.all().order_by('id')
        u = self.request.user
        if is_admin(u) or is_hr(u):
            return qs
        team_ids = manages_team_ids(u)
        if team_ids:
            return qs.filter(team_memberships__team_id__in=team_ids).distinct()
        return qs.filter(id=u.id)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()
    

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related('manager').all().order_by('name')
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticatedAndReadOnly,]
    
    
class TeamMembershipViewSet(viewsets.ModelViewSet):
    queryset = TeamMembership.objects.select_related('user', 'team').all().order_by('id')
    serializer_class = TeamMembershipSerializer
    permission_classes = [IsAuthenticatedAndReadOnly, IsAdminOrHr]