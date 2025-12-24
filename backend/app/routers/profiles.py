from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..auth import get_current_user, get_db

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=list[schemas.ProfileOut])
def list_profiles(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Profile).filter(models.Profile.user_id == current_user.id).all()


@router.post("", response_model=schemas.ProfileOut)
def create_profile(profile: schemas.ProfileCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    obj = models.Profile(user_id=current_user.id, **profile.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{profile_id}", response_model=schemas.ProfileOut)
def get_profile(profile_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.query(models.Profile).filter(models.Profile.id == profile_id, models.Profile.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Profile not found")
    return obj


@router.put("/{profile_id}", response_model=schemas.ProfileOut)
def update_profile(
    profile_id: int,
    profile: schemas.ProfileUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj = db.query(models.Profile).filter(models.Profile.id == profile_id, models.Profile.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in profile.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{profile_id}")
def delete_profile(profile_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.query(models.Profile).filter(models.Profile.id == profile_id, models.Profile.user_id == current_user.id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(obj)
    db.commit()
    return {"status": "deleted"}
