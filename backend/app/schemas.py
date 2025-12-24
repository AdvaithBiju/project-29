import datetime as dt
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class ProfileBase(BaseModel):
    name: str
    dob: Optional[dt.date] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    location_country: Optional[str] = None
    conditions: List[str] = []
    meds: List[str] = []


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int

    class Config:
        orm_mode = True


class BiomarkerOut(BaseModel):
    id: int
    test_name_raw: str
    test_name_norm: str
    value_float: float
    unit: str
    ref_low: float | None
    ref_high: float | None
    status: str
    notes: dict

    class Config:
        orm_mode = True


class ReportOut(BaseModel):
    id: int
    report_date: Optional[dt.date] = None
    file_path: str
    extracted_identity: dict
    identity_confirmed: bool
    created_at: dt.datetime
    biomarkers: List[BiomarkerOut] = []

    class Config:
        orm_mode = True


class IdentityConfirmation(BaseModel):
    confirmed: bool
    move_to_profile_id: Optional[int] = None


class InsightComparison(BaseModel):
    prev_value: float | None = None
    delta: float | None = None
    pct_change: float | None = None
    trend: str | None = None


class BiomarkerInsight(BaseModel):
    test_name: str
    standard_code: Optional[str] = None
    value: float
    unit: str
    ref_low: float | None
    ref_high: float | None
    status: str
    explanation: str
    lifestyle_tips: List[str]
    red_flags: List[str]
    compare_to_previous: InsightComparison


class InsightResponse(BaseModel):
    report_id: int
    biomarkers: List[BiomarkerInsight]
    overall_summary: dict
    disclaimers: List[str]
