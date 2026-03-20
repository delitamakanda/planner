from rest_framework import serializers
from accounts.models import Team, TeamMembership, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'timezone', 'weekly_working_hours', 'start_date']
        read_only_fields = ['id']
    
class TeamSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(source='manager', write_only=True, required=False, allow_null=True, queryset=User.objects.all())
    
    class Meta:
        model = Team
        fields = ['id', 'name','manager', 'manager_id', 'created_at']
        read_only_fields = ['id', 'created_at']
        

class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    
    user_id = serializers.PrimaryKeyRelatedField(source='user', write_only=True, required=False, allow_null=True, queryset=User.objects.all())
    team_id = serializers.PrimaryKeyRelatedField(source='team', write_only=True, required=False, allow_null=True, queryset=Team.objects.all())
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'user_id', 'team', 'team_id', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']