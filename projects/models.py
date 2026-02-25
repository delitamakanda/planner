from django.db import models
from django.utils import timezone

class Client(models.Model):
    name = models.CharField(max_length=100, unique=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Brouillon'
        PENDING = 'Pending', 'En attente'
        IN_PROGRESS = 'In Progress', 'En cours'
        COMPLETED = 'Completed', 'Terminé'
        ARCHIVED = 'Archived', 'Archivé'
        
    client = models.ForeignKey("projects.Client", on_delete=models.PROTECT, related_name='projects')
    code = models.CharField(max_length=100, unique=True) # ex: PRJ-2026-001
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, related_name='owned_projects', null=True, blank=True)
    teams = models.ManyToManyField("accounts.Team", related_name='projects')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
        ]
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def make_code(self):
        self.code = f"PRJ-{timezone.now().year}-{self.pk:04d}"
        self.save()
    

class ProjectTask(models.Model):
    class Priority(models.TextChoices):
        LOW = 'Low', 'Faible'
        MEDIUM = 'Medium', 'Moyen'
        HIGH = 'High', 'Haute'
        CRITICAL = 'Critical', 'Critique'
    class TaskType(models.TextChoices):
        FEATURE = 'Feature', 'Fonctionnalité'
        BUG = 'Bug', 'Bug'
        TASK = 'Task', 'Tâche'
        RUN = 'Run', 'Exécution'
        DELIVERABLE = 'Deliverable', 'Livrable'
        OTHER = 'Other', 'Autre'
    
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name='tasks')
    parent = models.ForeignKey("projects.ProjectTask", on_delete=models.SET_NULL, related_name='children', null=True, blank=True)
    title = models.CharField(max_length=255)
    task_type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.TASK)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.LOW)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0) # cout h/jour ou tjm converti en h
    currency = models.CharField(max_length=10, default='EUR')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['project', 'task_type'])
        ]
        
    @property
    def estimated_cost(self):
        return (self.estimated_hours or 0) * (self.rate or 0)
    
    def __str__(self):
        return f"{self.project.code} / {self.title}"