from django.db import models
from django.utils import timezone

class Assignment(models.Model):
    class AllocationType(models.TextChoices):
        PERCENTAGE = 'Percentage', 'Pourcentage'
        HOURS_PER_DAY = 'Hours per Day', 'Heures par jour'
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='assignments')
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name='assignments')
    
    project_task = models.ForeignKey("projects.ProjectTask", on_delete=models.SET_NULL, related_name='assignments', null=True, blank=True)
    
    date_start = models.DateField()
    date_end = models.DateField()
    allocation_type = models.CharField(max_length=20, choices=AllocationType.choices, default=AllocationType.HOURS_PER_DAY)
    allocation_value = models.DecimalField(max_digits=6, decimal_places=2) # 0 - 100% or hours per day
    comment = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, related_name='created_assignments', null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['date_start', 'date_end', 'user']),
            models.Index(fields=['project', 'date_start', 'date_end']),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(date_end__gte=models.F("date_start")), name="assignment_date_end_gte_date_start"),
            models.CheckConstraint(condition=models.Q(allocation_value__gte=0), name='assignment_allocation_value_gte_0'),
        ]
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} {self.project.code} {self.date_start}->{self.date_end}"


        
