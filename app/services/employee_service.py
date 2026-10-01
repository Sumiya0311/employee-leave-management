from sqlalchemy.orm import Session
from app.models.employee import Employee
def create_employee(
    db: Session,
    employee_code: str,
    name: str,
    email: str,
    phone: str,
    department_id: int,
    designation: str,
    salary: float,
    date_of_joining,
    employment_type: str,
):
    existing_code = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .first()
    )

    if existing_code:
        return "employee_code_exists"

    existing_email = (
        db.query(Employee)
        .filter(Employee.email == email)
        .first()
    )

    if existing_email:
        return "email_exists"

    employee = Employee(
        employee_code=employee_code,
        name=name,
        email=email,
        phone=phone,
        department_id=department_id,
        designation=designation,
        salary=salary,
        date_of_joining=date_of_joining,
        employment_type=employment_type,
        is_active=True,
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    name: str | None = None,
    department_id: int | None = None,
    designation: str | None = None,
    employment_type: str | None = None,
    is_active: bool | None = None,
    sort_by: str = "employee_id",
    order: str = "asc",
):
    query = db.query(Employee)

    if name:
        query = query.filter(Employee.name.ilike(f"%{name}%"))

    if department_id:
        query = query.filter(
            Employee.department_id == department_id
        )

    if designation:
        query = query.filter(
            Employee.designation.ilike(f"%{designation}%")
        )

    if employment_type:
        query = query.filter(
            Employee.employment_type == employment_type
        )

    if is_active is not None:
        query = query.filter(
            Employee.is_active == is_active
        )

    allowed_sort_fields = {
        "employee_id": Employee.employee_id,
        "employee_code": Employee.employee_code,
        "name": Employee.name,
        "salary": Employee.salary,
        "date_of_joining": Employee.date_of_joining,
    }

    sort_column = allowed_sort_fields.get(
        sort_by,
        Employee.employee_id
    )

    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    return query.offset(skip).limit(limit).all()


def get_employee(
    db: Session,
    employee_id: int
):
    return (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )


def update_employee(
    db: Session,
    employee_id: int,
    employee_code: str,
    name: str,
    email: str,
    phone: str,
    department_id: int,
    designation: str,
    salary: float,
    date_of_joining,
    employment_type: str,
    is_active: bool,
):
    employee = get_employee(db, employee_id)

    if not employee:
        return None

    existing_code = (
        db.query(Employee)
        .filter(
            Employee.employee_code == employee_code,
            Employee.employee_id != employee_id
        )
        .first()
    )

    if existing_code:
        return "employee_code_exists"

    existing_email = (
        db.query(Employee)
        .filter(
            Employee.email == email,
            Employee.employee_id != employee_id
        )
        .first()
    )

    if existing_email:
        return "email_exists"

    employee.employee_code = employee_code
    employee.name = name
    employee.email = email
    employee.phone = phone
    employee.department_id = department_id
    employee.designation = designation
    employee.salary = salary
    employee.date_of_joining = date_of_joining
    employee.employment_type = employment_type
    employee.is_active = is_active

    db.commit()
    db.refresh(employee)

    return employee


def delete_employee(
    db: Session,
    employee_id: int
):
    employee = get_employee(db, employee_id)

    if not employee:
        return None

    # Soft delete
    employee.is_active = False

    db.commit()
    db.refresh(employee)

    return employee