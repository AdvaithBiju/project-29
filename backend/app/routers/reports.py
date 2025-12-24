import datetime as dt
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from .. import models, schemas
from ..auth import get_current_user, get_db
from ..services import parser
from ..storage import storage

router = APIRouter(prefix="/profiles/{profile_id}/reports", tags=["reports"])


@router.get("", response_model=list[schemas.ReportOut])
def list_reports(profile_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    _ensure_profile_owner(profile_id, current_user.id, db)
    return (
        db.query(models.Report)
        .filter(models.Report.profile_id == profile_id)
        .order_by(models.Report.created_at.desc())
        .all()
    )


@router.post("", response_model=schemas.ReportOut)
def upload_report(
    profile_id: int,
    report_date: dt.date | None = Form(None),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_profile_owner(profile_id, current_user.id, db)
    if file.content_type not in {"application/pdf", "image/png", "image/jpeg"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    content = file.file.read()
    if len(content) > 1024 * 1024 * 10:
        raise HTTPException(status_code=400, detail="File too large")
    filename = f"{uuid.uuid4()}_{file.filename}"
    file.file.seek(0)
    saved_path = storage.save(file.file, filename)
    text = parser.ReportParser.extract_text(Path(saved_path))
    identity = parser.ReportParser.parse_identity(text)
    profile = db.query(models.Profile).get(profile_id)
    mismatch = parser.ReportParser.identity_mismatch_score(profile.name, profile.sex, identity)
    biomarker_rows = parser.ReportParser.parse_biomarkers(text, sex=profile.sex)

    report_obj = models.Report(
        profile_id=profile_id,
        report_date=report_date,
        file_path=str(saved_path),
        extracted_identity=identity.__dict__,
        identity_confirmed=mismatch < 0.5,
    )
    db.add(report_obj)
    db.commit()
    db.refresh(report_obj)

    for row in biomarker_rows:
        biomarker = models.Biomarker(
            report_id=report_obj.id,
            test_name_raw=row.test_name_raw,
            test_name_norm=row.test_name_norm,
            value_float=row.value,
            unit=row.unit,
            ref_low=row.ref_low,
            ref_high=row.ref_high,
            status=row.status,
            notes={},
        )
        db.add(biomarker)
    db.commit()
    db.refresh(report_obj)
    return report_obj


@router.get("/{report_id}", response_model=schemas.ReportOut)
def get_report(profile_id: int, report_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    _ensure_profile_owner(profile_id, current_user.id, db)
    report = db.query(models.Report).filter_by(id=report_id, profile_id=profile_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{report_id}/confirm_identity")
def confirm_identity(
    profile_id: int,
    report_id: int,
    payload: schemas.IdentityConfirmation,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_profile_owner(profile_id, current_user.id, db)
    report = db.query(models.Report).filter_by(id=report_id, profile_id=profile_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if payload.move_to_profile_id:
        _ensure_profile_owner(payload.move_to_profile_id, current_user.id, db)
        report.profile_id = payload.move_to_profile_id
    report.identity_confirmed = payload.confirmed
    db.commit()
    return {"status": "updated"}


def _ensure_profile_owner(profile_id: int, user_id: int, db: Session):
    profile = db.query(models.Profile).filter_by(id=profile_id, user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
