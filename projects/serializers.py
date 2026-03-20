from rest_framework import  serializers

from accounts.models import User, Team
from projects.models import Project, Client, ProjectTask
from accounts.serializers import UserSerializer, TeamSerializer

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
        
class ProjectTaskSerializer(serializers.ModelSerializer):
    estimated_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectTask
        fields = ['id', 'project', 'parent', 'title', 'task_type', 'priority', 'estimated_hours', 'estimated_cost', 'rate', 'currency', 'notes', 'created_at',]
        read_only_fields = ['id', 'created_at', 'estimated_cost']
    
    def get_estimated_cost(self, obj):
        return obj.estimated_cost
    
class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(source='owner', write_only=True, required=False, allow_null=True,queryset=User.objects.all())
    
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(source='client', write_only=True, required=False, allow_null=True,queryset=Client.objects.all())
    
    teams = TeamSerializer(many=True, read_only=True)
    team_ids = serializers.PrimaryKeyRelatedField(source='teams', write_only=True, required=False, allow_null=True,queryset=Team.objects.all())
    
    class Meta:
        model = Project
        fields = ['id', 'owner', 'owner_id', 'client', 'client_id', 'teams', 'team_ids', 'code', 'name', 'status', 'start_date', 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the teams based on the user's team memberships'
        from accounts.models import User, Team
        # Check if the user is authenticated and has team memberships
        self.fields['owner_id'].queryset = User.objects.all()
        self.fields['team_ids'].queryset = Team.objects.all()