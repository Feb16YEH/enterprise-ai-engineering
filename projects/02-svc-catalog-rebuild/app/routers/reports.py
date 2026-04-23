from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

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

@router.get("", response_model=list[ReportSpecRead])
def list_reports(
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
) -> list[ReportSpec]:
    statement = select(ReportSpec).offset(offset).limit(limit)
    reports = session.exec(statement).all()
    return list(reports)

@router.get("/{report_id}", response_model=ReportSpecRead)
def get_report(
    report_id: int,
    session: Session = Depends(get_session),
) -> ReportSpec:
    report = session.get(ReportSpec, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return report
