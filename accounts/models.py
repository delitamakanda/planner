from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    timezone = models.CharField(max_length=100, default='Europe/Paris')
    weekly_working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=35)
    start_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    manager = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, related_name='manager_team', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    

class TeamMembership(models.Model):
    class Role(models.TextChoices):
        MANAGER = 'Manager', 'Manager'
        ADMIN = 'Admin', 'Admin'
        MEMBER = 'Member', 'Member'
        HR = 'HR', 'HR'
    
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey("accounts.Team", on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'team'], name='unique_team_membership')
        ]
        
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} -> {self.team.name} ({self.role})"
