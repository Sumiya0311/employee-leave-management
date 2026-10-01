from sqlalchemy.orm import Session
from app.models.department import Department
from app.models.employee import Employee
def create_department(
    db: Session,
    department_name: str,
    location: str
):
    existing = (
        db.query(Department)
        .filter(
            Department.department_name == department_name
        )
        .first()
    )

    if existing:
        return None

    department = Department(
        department_name=department_name,
        location=location,
        is_active=True
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


def get_departments(
    db: Session,
    skip: int = 0,
    limit: int = 10
):
    return (
        db.query(Department)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_department_by_id(
    db: Session,
    department_id: int
):
    return (
        db.query(Department)
        .filter(
            Department.department_id == department_id
        )
        .first()
    )


def update_department(
    db: Session,
    department_id: int,
    department_name: str,
    location: str,
    is_active: bool
):
    department = get_department_by_id(
        db,
        department_id
    )

    if not department:
        return None

    department.department_name = department_name
    department.location = location
    department.is_active = is_active

    db.commit()
    db.refresh(department)

    return department


def delete_department(
    db: Session,
    department_id: int
):
    department = get_department_by_id(
        db,
        department_id
    )

    if not department:
        return None

    active_employee = (
        db.query(Employee)
        .filter(
            Employee.department_id == department_id,
            Employee.is_active == True
        )
        .first()
    )

    if active_employee:
        return "has_active_employees"

    db.delete(department)
    db.commit()

    return "deleted"


def get_department_employees(
    db: Session,
    department_id: int
):
    return (
        db.query(Employee)
        .filter(
            Employee.department_id == department_id
        )
        .all()
    )