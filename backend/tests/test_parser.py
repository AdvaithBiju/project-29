from pathlib import Path
from app.services.parser import ReportParser


def test_parse_identity_pdf():
    text = Path("backend/tests/fixtures/pdf_text.txt").read_text()
    identity = ReportParser.parse_identity(text)
    assert identity.patient_name == "Alex Doe"
    assert identity.sex == "male"
    assert identity.age == 32
    assert identity.lab_id == "LAB-123"


def test_parse_biomarkers_pdf():
    text = Path("backend/tests/fixtures/pdf_text.txt").read_text()
    rows = ReportParser.parse_biomarkers(text, sex="male")
    names = {row.test_name_norm for row in rows}
    assert "hemoglobin" in names
    assert any(row.status == "HIGH" for row in rows if row.test_name_norm == "ldl")


def test_parse_biomarkers_ocr():
    text = Path("backend/tests/fixtures/ocr_text.txt").read_text()
    rows = ReportParser.parse_biomarkers(text, sex="female")
    hb = next(row for row in rows if row.test_name_norm.startswith("hemoglobin") or row.test_name_norm == "hb")
    assert hb.status == "LOW"
    tsh = next(row for row in rows if row.test_name_norm == "tsh")
    assert tsh.status == "HIGH"
