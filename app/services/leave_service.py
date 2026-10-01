from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.leave_request import LeaveRequest


LEAVE_BALANCE = {
    "Sick": 12,
    "Casual": 10,
    "Earned": 15
}


def calculate_working_days(
    start_date: date,
    end_date: date
):
    total = 0
    current = start_date

    while current <= end_date:
        if current.weekday() < 5:
            total += 1

        current += timedelta(days=1)

    return total


def get_employee(
    db: Session,
    employee_id: int
):
    return (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id
        )
        .first()
    )


def get_leave_balance(
    db: Session,
    employee_id: int,
    leave_type: str
):
    allowed_days = LEAVE_BALANCE[leave_type]

    approved_days = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.leave_type == leave_type,
            LeaveRequest.status == "Approved"
        )
        .all()
    )

    used_days = sum(
        leave.total_days
        for leave in approved_days
    )

    return max(
        0,
        allowed_days - used_days
    )


def has_overlapping_leave(
    db: Session,
    employee_id: int,
    start_date: date,
    end_date: date
):
    return (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status.in_(
                ["Pending", "Approved"]
            ),
            LeaveRequest.start_date <= end_date,
            LeaveRequest.end_date >= start_date
        )
        .first()
    )


def create_leave(
    db: Session,
    employee_id: int,
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str
):
    employee = get_employee(
        db,
        employee_id
    )

    if not employee:
        return "employee_not_found"

    if not employee.is_active:
        return "employee_inactive"

    total_days = calculate_working_days(
        start_date,
        end_date
    )

    if total_days <= 0:
        return "no_working_days"

    overlapping = has_overlapping_leave(
        db,
        employee_id,
        start_date,
        end_date
    )

    if overlapping:
        return "overlap"

    balance = get_leave_balance(
        db,
        employee_id,
        leave_type
    )

    if total_days > balance:
        return "insufficient_balance"

    leave = LeaveRequest(
        employee_id=employee_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        reason=reason,
        status="Pending"
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    return leave


def get_leaves(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status_filter: str | None = None,
    leave_type: str | None = None,
    employee_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None
):
    query = db.query(LeaveRequest)

    if status_filter:
        query = query.filter(
            LeaveRequest.status == status_filter
        )

    if leave_type:
        query = query.filter(
            LeaveRequest.leave_type == leave_type
        )

    if employee_id:
        query = query.filter(
            LeaveRequest.employee_id == employee_id
        )

    if from_date:
        query = query.filter(
            LeaveRequest.start_date >= from_date
        )

    if to_date:
        query = query.filter(
            LeaveRequest.end_date <= to_date
        )

    return (
        query
        .order_by(
            LeaveRequest.leave_id.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_leave(
    db: Session,
    leave_id: int
):
    return (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.leave_id == leave_id
        )
        .first()
    )


def get_employee_leaves(
    db: Session,
    employee_id: int
):
    return (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id
        )
        .order_by(
            LeaveRequest.leave_id.desc()
        )
        .all()
    )


def approve_leave(
    db: Session,
    leave_id: int,
    approved_by: int
):
    leave = get_leave(
        db,
        leave_id
    )

    if not leave:
        return None

    if leave.status != "Pending":
        return "invalid_status"

    leave.status = "Approved"
    leave.approved_by = approved_by

    db.commit()
    db.refresh(leave)

    return leave


def reject_leave(
    db: Session,
    leave_id: int,
    approved_by: int,
    rejection_reason: str
):
    leave = get_leave(
        db,
        leave_id
    )

    if not leave:
        return None

    if leave.status != "Pending":
        return "invalid_status"

    leave.status = "Rejected"
    leave.approved_by = approved_by
    leave.rejection_reason = rejection_reason

    db.commit()
    db.refresh(leave)

    return leave


def cancel_leave(
    db: Session,
    leave_id: int
):
    leave = get_leave(
        db,
        leave_id
    )

    if not leave:
        return None

    if leave.status != "Pending":
        return "invalid_status"

    leave.status = "Cancelled"

    db.commit()
    db.refresh(leave)

    return leave