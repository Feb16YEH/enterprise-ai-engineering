from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.models import ReportSpec, ReportSpecCreate, ReportSpecRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportSpecRead, status_code=status.HTTP_201_CREATED)
def create_report(
    report_create: ReportSpecCreate,
    session: Session = Depends(get_session),
) -> ReportSpec:
    report = ReportSpec.model_validate(report_create)
    session.add(report)
    session.commit()
    session.refresh(report)
    return report

