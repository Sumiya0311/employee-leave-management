from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services import employee_service
from app.auth.dependencies import (
    get_current_user,
    require_role
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


# CREATE EMPLOYEE


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=201
)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin", "HR")
    )
):
    if employee.date_of_joining > date.today():
        raise HTTPException(
            status_code=422,
            detail="Date of joining cannot be in the future"
        )

    result = employee_service.create_employee(
        db=db,
        employee_code=employee.employee_code,
        name=employee.name,
        email=employee.email,
        phone=employee.phone,
        department_id=employee.department_id,
        designation=employee.designation,
        salary=employee.salary,
        date_of_joining=employee.date_of_joining,
        employment_type=employee.employment_type,
    )

    if result == "employee_code_exists":
        raise HTTPException(
            status_code=409,
            detail="Employee code already exists"
        )

    if result == "email_exists":
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return result



# GET ALL EMPLOYEES


@router.get(
    "/",
    response_model=list[EmployeeResponse]
)
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: str | None = None,
    department_id: int | None = Query(
        None,
        gt=0
    ),
    designation: str | None = None,
    employment_type: str | None = None,
    is_active: bool | None = None,
    sort_by: str = "employee_id",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Employee can view only their own details
    if current_user.role == "Employee":
        if current_user.employee_id is None:
            return []

        employee = employee_service.get_employee(
            db,
            current_user.employee_id
        )

        if not employee:
            return []

        return [employee]

    return employee_service.get_employees(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        department_id=department_id,
        designation=designation,
        employment_type=employment_type,
        is_active=is_active,
        sort_by=sort_by,
        order=order,
    )


# GET EMPLOYEE BY ID


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = employee_service.get_employee(
        db,
        employee_id
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Employee can access only their own details
    if current_user.role == "Employee":
        if current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="You can access only your own details"
            )

    return employee


# UPDATE EMPLOYEE

@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_employee = employee_service.get_employee(
        db,
        employee_id
    )

    if not existing_employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Employee can update only their own details
    if current_user.role == "Employee":
        if current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="You can update only your own details"
            )

    # Only Admin and HR can manage other employees
    if current_user.role not in {
        "Admin",
        "HR",
        "Employee"
    }:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update employee details"
        )

    if employee.date_of_joining > date.today():
        raise HTTPException(
            status_code=422,
            detail="Date of joining cannot be in the future"
        )

    result = employee_service.update_employee(
        db=db,
        employee_id=employee_id,
        employee_code=employee.employee_code,
        name=employee.name,
        email=employee.email,
        phone=employee.phone,
        department_id=employee.department_id,
        designation=employee.designation,
        salary=employee.salary,
        date_of_joining=employee.date_of_joining,
        employment_type=employee.employment_type,
        is_active=employee.is_active,
    )

    if result == "employee_code_exists":
        raise HTTPException(
            status_code=409,
            detail="Employee code already exists"
        )

    if result == "email_exists":
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return result



# DELETE / SOFT DELETE EMPLOYEE

@router.delete(
    "/{employee_id}"
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin", "HR")
    )
):
    employee = employee_service.delete_employee(
        db,
        employee_id
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return {
        "message": "Employee deactivated successfully"
    }