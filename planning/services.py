from __future__ import annotations
from django.db import transaction
from planning.models import Assignment

class PlanningService:
    @classmethod
    @transaction.atomic
    def create_assignment(*, data: dict, user) -> Assignment:
        return Assignment.objects.create(created_by=user, **data)
    
    @classmethod
    @transaction.atomic
    def update_assignment(*, assignment: Assignment, data: dict) -> Assignment:
        for key, value in data.items():
            setattr(assignment, key, value)
        assignment.save()
        return assignment