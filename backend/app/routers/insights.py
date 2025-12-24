from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from .. import models, schemas
from ..auth import get_current_user, get_db
from ..services.insights import build_insights

router = APIRouter(prefix="/profiles/{profile_id}/reports/{report_id}", tags=["insights"])


@router.get("/insights", response_model=schemas.InsightResponse)
def get_insights(profile_id: int, report_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    _ensure_profile_owner(profile_id, current_user.id, db)
    report = db.query(models.Report).filter_by(id=report_id, profile_id=profile_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    biomarkers = db.query(models.Biomarker).filter_by(report_id=report_id).all()
    prev_report = (
        db.query(models.Report)
        .filter(models.Report.profile_id == profile_id, models.Report.id != report_id)
        .order_by(models.Report.created_at.desc())
        .first()
    )
    prev_rows = db.query(models.Biomarker).filter_by(report_id=prev_report.id).all() if prev_report else []
    response = build_insights(biomarkers, prev_rows)
    return schemas.InsightResponse(report_id=report_id, **response)


@router.get("/sbar.pdf")
def download_sbar(profile_id: int, report_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    from ..services.sbar import generate_sbar_pdf

    profile = _ensure_profile_owner(profile_id, current_user.id, db)
    report = db.query(models.Report).filter_by(id=report_id, profile_id=profile_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    biomarkers = db.query(models.Biomarker).filter_by(report_id=report_id).all()
    pdf_bytes = generate_sbar_pdf(profile, report, biomarkers)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=sbar.pdf"})


def _ensure_profile_owner(profile_id: int, user_id: int, db: Session):
    profile = db.query(models.Profile).filter_by(id=profile_id, user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
