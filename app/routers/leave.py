from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.leave import (
    LeaveCreate,
    LeaveRejectRequest,
    LeaveResponse
)
from app.services import leave_service
from app.auth.dependencies import (
    get_current_user,
    require_role
)


router = APIRouter(
    prefix="/leaves",
    tags=["Leaves"]
)


# =========================
# APPLY FOR LEAVE
# =========================

@router.post(
    "/",
    response_model=LeaveResponse,
    status_code=201
)
def create_leave(
    leave: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Employee can apply only for themselves
    if current_user.role == "Employee":
        if current_user.employee_id != leave.employee_id:
            raise HTTPException(
                status_code=403,
                detail="Employees can apply leave only for themselves"
            )

    if leave.start_date < date.today():
        raise HTTPException(
            status_code=422,
            detail="Leave cannot be applied for past dates"
        )

    if leave.end_date < leave.start_date:
        raise HTTPException(
            status_code=422,
            detail="End date cannot be before start date"
        )

    result = leave_service.create_leave(
        db=db,
        employee_id=leave.employee_id,
        leave_type=leave.leave_type,
        start_date=leave.start_date,
        end_date=leave.end_date,
        reason=leave.reason
    )

    if result == "employee_not_found":
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    if result == "employee_inactive":
        raise HTTPException(
            status_code=400,
            detail="Inactive employee cannot apply for leave"
        )

    if result == "no_working_days":
        raise HTTPException(
            status_code=400,
            detail="Selected dates contain no working days"
        )

    if result == "overlap":
        raise HTTPException(
            status_code=409,
            detail="Leave dates overlap with an existing leave request"
        )

    if result == "insufficient_balance":
        raise HTTPException(
            status_code=400,
            detail="Insufficient leave balance"
        )

    return result


# =========================
# GET ALL LEAVES
# =========================

@router.get(
    "/",
    response_model=list[LeaveResponse]
)
def get_leaves(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: str | None = None,
    leave_type: str | None = None,
    employee_id: int | None = Query(None, gt=0),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Employee can see only their own leaves
    if current_user.role == "Employee":
        employee_id = current_user.employee_id

    if from_date and to_date:
        if from_date > to_date:
            raise HTTPException(
                status_code=422,
                detail="from_date cannot be after to_date"
            )

    return leave_service.get_leaves(
        db=db,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        leave_type=leave_type,
        employee_id=employee_id,
        from_date=from_date,
        to_date=to_date
    )


# =========================
# GET LEAVE BY ID
# =========================

@router.get(
    "/{leave_id}",
    response_model=LeaveResponse
)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = leave_service.get_leave(
        db,
        leave_id
    )

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    # Employee can see only their own leave
    if current_user.role == "Employee":
        if current_user.employee_id != leave.employee_id:
            raise HTTPException(
                status_code=403,
                detail="You can access only your own leave requests"
            )

    return leave


# =========================
# GET EMPLOYEE LEAVES
# =========================

@router.get(
    "/employees/{employee_id}/leaves",
    response_model=list[LeaveResponse]
)
def get_employee_leaves(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "Employee":
        if current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="You can access only your own leave requests"
            )

    employee = leave_service.get_employee(
        db,
        employee_id
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return leave_service.get_employee_leaves(
        db,
        employee_id
    )


# =========================
# GET LEAVE BALANCE
# =========================

@router.get(
    "/employees/{employee_id}/leave-balance"
)
def get_leave_balance(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "Employee":
        if current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="You can access only your own leave balance"
            )

    employee = leave_service.get_employee(
        db,
        employee_id
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return {
        "employee_id": employee_id,
        "Sick": leave_service.get_leave_balance(
            db,
            employee_id,
            "Sick"
        ),
        "Casual": leave_service.get_leave_balance(
            db,
            employee_id,
            "Casual"
        ),
        "Earned": leave_service.get_leave_balance(
            db,
            employee_id,
            "Earned"
        )
    }


# APPROVE LEAVE


@router.put(
    "/{leave_id}/approve",
    response_model=LeaveResponse
)
def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin", "HR")
    )
):
    leave = leave_service.get_leave(
        db,
        leave_id
    )

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    # HR cannot approve their own leave
    if (
        current_user.role == "HR"
        and current_user.employee_id == leave.employee_id
    ):
        raise HTTPException(
            status_code=403,
            detail="HR cannot approve their own leave"
        )

    result = leave_service.approve_leave(
        db,
        leave_id,
        current_user.user_id
    )

    if result == "invalid_status":
        raise HTTPException(
            status_code=400,
            detail="Only pending leave requests can be approved"
        )

    return result

# REJECT LEAVE


@router.put(
    "/{leave_id}/reject",
    response_model=LeaveResponse
)
def reject_leave(
    leave_id: int,
    request: LeaveRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin", "HR")
    )
):
    leave = leave_service.get_leave(
        db,
        leave_id
    )

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    # HR cannot reject their own leave
    if (
        current_user.role == "HR"
        and current_user.employee_id == leave.employee_id
    ):
        raise HTTPException(
            status_code=403,
            detail="HR cannot reject their own leave"
        )

    result = leave_service.reject_leave(
        db,
        leave_id,
        current_user.user_id,
        request.rejection_reason
    )

    if result == "invalid_status":
        raise HTTPException(
            status_code=400,
            detail="Only pending leave requests can be rejected"
        )

    return result



# CANCEL LEAVE


@router.put(
    "/{leave_id}/cancel",
    response_model=LeaveResponse
)
def cancel_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave = leave_service.get_leave(
        db,
        leave_id
    )

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    # Only the employee who applied can cancel
    if current_user.employee_id != leave.employee_id:
        raise HTTPException(
            status_code=403,
            detail="You can cancel only your own leave request"
        )

    result = leave_service.cancel_leave(
        db,
        leave_id
    )

    if result == "invalid_status":
        raise HTTPException(
            status_code=400,
            detail="Only pending leave requests can be cancelled"
        )

    return result