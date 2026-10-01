from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest


def get_dashboard(db: Session):

    total_employees = (
        db.query(Employee)
        .count()
    )

    active_employees = (
        db.query(Employee)
        .filter(Employee.is_active == True)
        .count()
    )

    employees_per_department = (
        db.query(
            Department.department_name,
            func.count(Employee.employee_id)
        )
        .outerjoin(
            Employee,
            Employee.department_id == Department.department_id
        )
        .group_by(Department.department_id)
        .all()
    )

    pending_leave_requests = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Pending"
        )
        .count()
    )

    today = date.today()

    employees_on_leave_today = (
        db.query(LeaveRequest.employee_id)
        .filter(
            LeaveRequest.status == "Approved",
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today
        )
        .distinct()
        .count()
    )

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "employees_per_department": [
            {
                "department": department_name,
                "employee_count": employee_count
            }
            for department_name, employee_count
            in employees_per_department
        ],
        "pending_leave_requests": pending_leave_requests,
        "employees_on_leave_today": employees_on_leave_today
    }


def get_leave_summary(
    db: Session,
    year: int,
    month: int
):
    results = (
        db.query(
            LeaveRequest.leave_type,
            LeaveRequest.status,
            func.count(LeaveRequest.leave_id)
        )
        .filter(
            func.year(LeaveRequest.start_date) == year,
            func.month(LeaveRequest.start_date) == month
        )
        .group_by(
            LeaveRequest.leave_type,
            LeaveRequest.status
        )
        .all()
    )

    return [
        {
            "leave_type": leave_type,
            "status": status,
            "count": count
        }
        for leave_type, status, count in results
    ]