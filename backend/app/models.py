import datetime as dt
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    dob = Column(Date)
    sex = Column(String)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    location_country = Column(String)
    conditions = Column(JSON, default=list)
    meds = Column(JSON, default=list)

    user = relationship("User", back_populates="profiles")
    reports = relationship("Report", back_populates="profile", cascade="all, delete-orphan")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    report_date = Column(Date)
    file_path = Column(String, nullable=False)
    extracted_identity = Column(JSON, default=dict)
    identity_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    profile = relationship("Profile", back_populates="reports")
    biomarkers = relationship("Biomarker", back_populates="report", cascade="all, delete-orphan")


class Biomarker(Base):
    __tablename__ = "biomarkers"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    test_name_raw = Column(String)
    test_name_norm = Column(String)
    value_float = Column(Float)
    unit = Column(String)
    ref_low = Column(Float)
    ref_high = Column(Float)
    status = Column(String)
    notes = Column(JSON, default=dict)

    report = relationship("Report", back_populates="biomarkers")
