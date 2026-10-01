from fastapi import FastAPI
from app.routers import department, employee, auth, leave, report

app = FastAPI(
    title="Employee Leave Management System",
    description="Employee Leave Management API",
    version="1.0.0"
)

app.include_router(department.router)
app.include_router(employee.router)
app.include_router(auth.router)
app.include_router(leave.router)
app.include_router(report.router)


@app.get("/")
def home():
    return {
        "message": "Employee Leave Management System API is running"
    }