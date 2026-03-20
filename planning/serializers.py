from rest_framework import serializers
from planning.models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            'id',
            'user',
            'project',
            'project_task',
            'date_start',
            'date_end',
            'allocation_type',
            'allocation_value',
            'comment',
            'created_at',
            'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by']