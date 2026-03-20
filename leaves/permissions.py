from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import TeamMembership

def _has_role(user, roles: set[str]) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return TeamMembership.objects.filter(user=user, role__in=list(roles)).exists()

def is_admin(user) -> bool:
    return _has_role(user, {TeamMembership.Role.ADMIN})

def is_hr(user) -> bool:
    return _has_role(user, {TeamMembership.Role.HR})

def manages_team_ids(user) -> list[int]:
    return list(
        TeamMembership.objects.filter(user=user, role=TeamMembership.Role.MANAGER).values_list('team_id', flat=True)
    )


class LeaveRequestPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if view.action == "create":
            return True
        if view.action in ["submit", "cancel"]:
            return True
        if view.action in ["approve", "reject", "update", "partial_update", "destroy"]:
            return is_admin(request.user) or is_hr(request.user) or bool(manages_team_ids(request.user))
        return True
    
    def has_object_permission(self, request, view, obj):
        u = request.user
        
        if is_admin(u) or is_hr(u):
            return True
        
        if obj.user == u.id:
            if request.method in SAFE_METHODS:
                return True
            if view.action in ["submit", "cancel"]:
                return True
            return False
        
        team_ids = manages_team_ids(u)
        if not team_ids:
            return False
        
        in_scope = obj.user.team_memberships.filter(team_id__in=team_ids).exists()
        if not in_scope:
            return False
        
        if request.method in SAFE_METHODS:
            return True
        return view.action in ["update", "partial_update", "destroy", "approve", "reject"]