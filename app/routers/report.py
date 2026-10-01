from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.auth.dependencies import require_role
from app.services import report_service


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin", "HR")
    )
):
    return report_service.get_dashboard(db)


@router.get("/leave-summary")
def leave_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("Admin", "HR")
    )
):
    return report_service.get_leave_summary(
        db,
        year,
        month
    )