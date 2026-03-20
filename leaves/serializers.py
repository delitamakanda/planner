from rest_framework import serializers
from leaves.models import LeaveType, LeaveBalance, LeaveRequest

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'code', 'name', 'requires_hr_approval', 'count_weekends']
        

class LeaveBalanceSerializer(serializers.ModelSerializer):
    remaining = serializers.SerializerMethodField()
    leave_type = LeaveTypeSerializer(read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = ['id', 'user', 'leave_type', 'acquired', 'used', 'remaining', 'updated_at']
        read_only_fields = ['id', 'updated_at', 'remaining']
        
    def get_remaining(self, obj):
        return obj.remaining
    
    
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = [
            'id',
            'user',
            'leave_type',
            'date_start',
            'date_end',
            'start_half_day',
            'end_half_day',
            'status',
            'reason',
            'manager_approver',
            'hr_approver',
            'submitted_at',
            'decided_at',
            'created_at',
        ]
        read_only_fields = ['id', 'manager_approver', 'hr_approver', 'submitted_at', 'decided_at', 'created_at']
