from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from rest_framework.permissions import BasePermission, SAFE_METHODS

from django.db.models import Q
from accounts.models import TeamMembership

@dataclass(frozen=True)
class Role:
    ADMIN: str = TeamMembership.Role.ADMIN
    MANAGER: str = TeamMembership.Role.MANAGER
    EMPLOYEE: str = TeamMembership.Role.MEMBER
    HR: str = TeamMembership.Role.HR
    
    
def user_roles_q(user_id: int, roles: Iterable[str]) -> Q:
    return Q(team_membership__user_id=user_id, team_membership__role__in=list(roles))

def is_admin(user) -> bool:
    return user and user.is_authenticated and (
        user.is_superuser or TeamMembership.objects.filter(user=user, role=TeamMembership.Role.ADMIN).exists()
    )

def is_hr(user) -> bool:
    return user and user.is_authenticated and (
        user.is_superuser or TeamMembership.objects.filter(user=user, role=TeamMembership.Role.HR).exists()
    )

def manages_team(user) -> bool:
    return user and user.is_authenticated and (
        TeamMembership.objects.filter(user=user, role__in=[TeamMembership.Role.ADMIN, TeamMembership.Role.MANAGER]).exists()
    )

def manages_team_ids(user) -> list[int]:
    return  list(TeamMembership.objects.filter(user=user, role__in=[TeamMembership.Role.ADMIN, TeamMembership.Role.MANAGER]).values_list('team_id', flat=True))


class IsAuthenticatedAndReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return False
    
    
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)
    
    
class IsAdminOrHr(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user) or is_hr(request.user)
    
    
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return manages_team(request.user)
    