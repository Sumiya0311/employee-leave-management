from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate
)
from app.services import department_service
from app.auth.dependencies import get_current_user, require_role


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=201
)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin")
    )
):
    result = department_service.create_department(
        db,
        department.department_name,
        department.location
    )

    if result is None:
        raise HTTPException(
            status_code=409,
            detail="Department already exists"
        )

    return result


@router.get(
    "/",
    response_model=list[DepartmentResponse]
)
def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return department_service.get_departments(
        db,
        skip,
        limit
    )


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    department = department_service.get_department_by_id(
        db,
        department_id
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department


@router.get(
    "/{department_id}/employees"
)
def get_department_employees(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    department = department_service.get_department_by_id(
        db,
        department_id
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department_service.get_department_employees(
        db,
        department_id
    )


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse
)
def update_department(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin")
    )
):
    existing = department_service.get_department_by_id(
        db,
        department_id
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    result = department_service.update_department(
        db,
        department_id,
        department.department_name,
        department.location,
        department.is_active
    )

    return result


@router.delete(
    "/{department_id}"
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin")
    )
):
    result = department_service.delete_department(
        db,
        department_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    if result == "has_active_employees":
        raise HTTPException(
            status_code=409,
            detail="Cannot delete department with active employees"
        )

    return {
        "message": "Department deleted successfully"
    }