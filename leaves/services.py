from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from leaves.models import LeaveRequest, LeaveBalance, LeaveType

def business_days_count(start_date: date, end_date: date) -> int:
    "compte lun-ven"
    if end_date < start_date:
        return 0
    days = 0
    cur = start_date
    while cur <= end_date:
        if cur.weekday() < 5:  # Monday to Friday
            days += 1
        cur += timedelta(days=1)
    return days

def compute_leave_units(lr: LeaveRequest) -> Decimal:
    """
    mvp jours ouvrés (lundi à vendredi) + gestion mi-journées
    - start_half_day = True -> 0.5
    - end_half_day = True -> 0.5
    """
    units = Decimal(business_days_count(lr.date_start, lr.date_end))
    if units == 0:
        return Decimal(0)
    if lr.start_half_day:
        units -= Decimal(0.5)
    if lr.end_half_day:
        units -= Decimal(0.5)
    return units

@dataclass(frozen=True)
class BalanceDelta:
    used_delta: Decimal
    acquired_delta: Decimal = Decimal(0)
    
class LeaveBalanceService:
    @staticmethod
    def get_or_create_balance_for_update(*, user_id: int, year: int, leave_type: LeaveType) -> LeaveBalance:
        qs = LeaveBalance.objects.select_for_update().filter(user_id=user_id, year=year, leave_type=leave_type)
        balance = qs.first()
        if balance:
            return balance
        return LeaveBalance.objects.create(user_id=user_id, year=year, leave_type=leave_type, acquired=Decimal(0), used=Decimal(0))
    
    @staticmethod
    def apply_delta(*, balance: LeaveBalance, delta: BalanceDelta) -> LeaveBalance:
        balance.used = (balance.used or Decimal(0)) + delta.used_delta
        balance.acquired = (balance.acquired or Decimal(0)) + delta.acquired_delta
        if balance.used < 0:
            balance.used = Decimal(0)
        balance.save(update_fields=['used', 'acquired', 'updated_at'])
        return balance
    
    
class LeaveService:
    """
    - Approved => increment used
    - Rejected / Canceled => decrement used si deja approved
    - PENDING/SUBMITTED => no change
    """
    @staticmethod
    def submit(*, lr: LeaveRequest, user) -> LeaveRequest:
        if lr.status != LeaveRequest.Status.PENDING:
            raise ValueError("Invalid status")
        
        if user.id != lr.user.id and not user.is_superuser:
            raise PermissionError("Forbidden")
        
        lr.status = LeaveRequest.Status.SUBMITTED
        lr.submitted_at = timezone.now()
        lr.save(update_fields=['status','submitted_at'])
        return lr
    
    @staticmethod
    @transaction.atomic
    def approve(*, lr: LeaveRequest, user, approved_as: str) -> LeaveRequest:
        """
        approved_as manager or hr
        """
        if lr.status!= LeaveRequest.Status.SUBMITTED:
            raise ValueError("Invalid status")
        
        lr.status = LeaveRequest.Status.APPROVED
        lr.decided_at = timezone.now()
        if approved_as == "manager":
            lr.manager_approver = user
        else:
            lr.hr_approver = user
        lr.save(update_fields=['status','manager_approver','hr_approver','decided_at'])
        
        units = compute_leave_units(lr)
        if units > 0:
            balance = LeaveBalanceService.get_or_create_balance_for_update(user_id=lr.user.id, year=lr.date_start.year, leave_type=lr.leave_type)
            LeaveBalanceService.apply_delta(balance=balance, delta=BalanceDelta(used_delta=units))
        return lr
    
    @staticmethod
    @transaction.atomic
    def reject(*, lr: LeaveRequest, user, rejected_as: str) -> LeaveRequest:
        if lr.status!= LeaveRequest.Status.SUBMITTED:
            raise ValueError("Invalid status")
        lr.status = LeaveRequest.Status.REJECTED
        lr.decided_at = timezone.now()
        if rejected_as == "manager":
            lr.manager_approver = user
        else:
            lr.hr_approver = user
        lr.save(update_fields=['status','manager_approver','hr_approver','decided_at'])
        return lr
    
    @staticmethod
    @transaction.atomic
    def cancel(*, lr: LeaveRequest, user) -> LeaveRequest:
        if lr.status not in [LeaveRequest.Status.SUBMITTED, LeaveRequest.Status.PENDING]:
            raise ValueError("Invalid status")
        
        if user.id!= lr.user.id and not user.is_superuser:
            raise PermissionError("Forbidden")
        was_approved = lr.status == LeaveRequest.Status.APPROVED
        lr.status = LeaveRequest.Status.CANCELLED
        lr.decided_at = timezone.now()
        lr.save(update_fields=['status', 'decided_at'])
        
        if was_approved:
            units = compute_leave_units(lr)
            if units > 0:
                balance = LeaveBalanceService.get_or_create_balance_for_update(user_id=lr.user.id, year=lr.date_start.year, leave_type=lr.leave_type)
                LeaveBalanceService.apply_delta(balance=balance, delta=BalanceDelta(used_delta=-units))
        return lr
    