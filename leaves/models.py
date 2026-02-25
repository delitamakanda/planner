from django.db import models
from django.utils import timezone

class LeaveType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    requires_hr_approval = models.BooleanField(default=False)
    count_weekends = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
class LeaveBalance(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='leave_balances')
    year = models.PositiveIntegerField()
    leave_type = models.ForeignKey("LeaveType", on_delete=models.CASCADE, related_name='balances')
    acquired = models.DecimalField(max_digits=6, decimal_places=2, default=0) # in days
    used = models.DecimalField(max_digits=6, decimal_places=2, default=0) # in days
    
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'year', 'leave_type'], name='unique_leave_balance')
        ]
        indexes = [
            models.Index(fields=['user', 'year']),
        ]
        
    @property
    def remaining(self):
        return self.acquired - self.used
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.year}) - {self.leave_type.name}"
    
class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'En attente'
        APPROVED = 'Approved', 'Approuvé'
        REJECTED = 'Rejected', 'Refusé'
        CANCELLED = 'Cancelled', 'Annulé'
        SUBMITTED = 'Submitted', 'Soumis'
    
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey("LeaveType", on_delete=models.PROTECT, related_name='requests')
    
    date_start = models.DateField()
    date_end = models.DateField()
    
    start_half_day = models.BooleanField(default=False)
    end_half_day = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reason = models.CharField(max_length=255, blank=True)
    
    manager_approver = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, related_name='manager_approvals', null=True, blank=True)
    hr_approver = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, related_name='hr_approvals', null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'date_start', 'date_end', 'status']),
            models.Index(fields=['status', 'date_start', 'date_end']),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(date_end__gte=models.F("date_start")), name="leave_request_date_end_gte_date_start"),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.leave_type.name} {self.date_start}->{self.date_end}"