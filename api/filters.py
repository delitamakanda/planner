import django_filters
from planning.models import Assignment
from leaves.models import LeaveRequest
from projects.models import Project

class AssignmentFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(field_name='date_start', lookup_expr='gte')
    to_date = django_filters.DateFilter(field_name='date_end', lookup_expr='lte')
    team = django_filters.NumberFilter(method='filter_team', lookup_expr='exact')
    project = django_filters.NumberFilter(method='project_id', lookup_expr='exact')
    user = django_filters.NumberFilter(method='user_id', lookup_expr='exact')
    
    class Meta:
        model = Assignment
        fields = ['project_id', 'user_id', 'team', 'from_date', 'to_date', 'user']
    
    def filter_team(self, queryset, name, value):
        return queryset.filter(user__team_memberships__team_id=value)
    
class LeaveRequestFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(field_name='date_start', lookup_expr='gte')
    to_date = django_filters.DateFilter(field_name='date_end', lookup_expr='lte')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    user = django_filters.NumberFilter(method='user_id', lookup_expr='exact')
    
    class Meta:
        model = LeaveRequest
        fields = ['status', 'user', 'from_date', 'to_date']
        
class ProjectFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    team = django_filters.NumberFilter(method='teams__id', lookup_expr='exact')
    
    class Meta:
        model = Project
        fields = ['status', 'team']
