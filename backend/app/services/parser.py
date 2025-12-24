import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import pdfplumber
import pytesseract
from PIL import Image
from rapidfuzz import fuzz

# Minimal reference ranges keyed by normalized name and sex.
REFERENCE_RANGES = {
    "hemoglobin": {"male": (13.5, 17.5), "female": (12.0, 15.5)},
    "wbc": {"any": (4.0, 11.0)},
    "rbc": {"any": (4.2, 6.1)},
    "hba1c": {"any": (4.0, 5.6)},
    "ldl": {"any": (0, 130)},
    "hdl": {"any": (40, 90)},
    "triglycerides": {"any": (0, 150)},
    "ferritin": {"any": (20, 250)},
    "tsh": {"any": (0.4, 4.0)},
    "creatinine": {"any": (0.6, 1.3)},
    "glucose": {"any": (70, 140)},
}

NORMALIZATION_MAP = {
    "hb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "wbc": "wbc",
    "white blood cell": "wbc",
    "rbc": "rbc",
    "hba1c": "hba1c",
    "a1c": "hba1c",
    "ldl": "ldl",
    "hdl": "hdl",
    "tg": "triglycerides",
    "triglycerides": "triglycerides",
    "ferritin": "ferritin",
    "tsh": "tsh",
    "creatinine": "creatinine",
    "glucose": "glucose",
}


@dataclass
class Identity:
    patient_name: Optional[str]
    sex: Optional[str]
    age: Optional[int]
    dob: Optional[str]
    collection_date: Optional[str]
    lab_id: Optional[str]


@dataclass
class BiomarkerRow:
    test_name_raw: str
    test_name_norm: str
    value: float
    unit: str
    ref_low: Optional[float]
    ref_high: Optional[float]
    status: str


class ReportParser:
    @staticmethod
    def extract_text(file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            try:
                with pdfplumber.open(str(file_path)) as pdf:
                    pages_text = [page.extract_text() or "" for page in pdf.pages]
                text = "\n".join(pages_text)
                if text.strip():
                    return text
                images = []
                for page in pdf.pages:
                    images.extend(page.images)
                if images:
                    with pdfplumber.open(str(file_path)) as pdf_for_image:
                        merged = Image.new("RGB", pdf_for_image.pages[0].to_image().original.size)
                        merged.paste(pdf_for_image.pages[0].to_image().original)
                        return pytesseract.image_to_string(merged)
            except Exception:
                pass
        elif suffix in {".png", ".jpg", ".jpeg"}:
            try:
                image = Image.open(file_path)
                return pytesseract.image_to_string(image)
            except Exception:
                pass
        try:
            return file_path.read_text()
        except Exception:
            return ""

    @staticmethod
    def parse_identity(text: str) -> Identity:
        name_match = re.search(r"Patient\s*Name[:\-]?\s*([A-Za-z\s]+)", text, re.IGNORECASE)
        sex_match = re.search(r"Sex[:\-]?\s*(Male|Female|M|F)", text, re.IGNORECASE)
        age_match = re.search(r"Age[:\-]?\s*(\d{1,3})", text, re.IGNORECASE)
        dob_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        collection_match = re.search(r"Collected[:\-]?\s*([\d\-\/]{8,10})", text, re.IGNORECASE)
        lab_match = re.search(r"Lab\s*ID[:\-]?\s*([A-Za-z0-9-]+)", text, re.IGNORECASE)

        sex = sex_match.group(1) if sex_match else None
        if sex:
            sex = "male" if sex.lower().startswith("m") else "female"

        return Identity(
            patient_name=name_match.group(1).strip() if name_match else None,
            sex=sex,
            age=int(age_match.group(1)) if age_match else None,
            dob=dob_match.group(1) if dob_match else None,
            collection_date=collection_match.group(1) if collection_match else None,
            lab_id=lab_match.group(1) if lab_match else None,
        )

    @staticmethod
    def _normalize_name(raw: str) -> Tuple[str, str]:
        key = raw.lower().strip()
        for variant, norm in NORMALIZATION_MAP.items():
            if variant in key:
                return raw.strip(), norm
        return raw.strip(), key

    @staticmethod
    def _parse_range(range_part: str) -> Tuple[Optional[float], Optional[float]]:
        if not range_part:
            return None, None
        between = re.search(r"([\d\.]+)\s*[\-–]\s*([\d\.]+)", range_part)
        if between:
            return float(between.group(1)), float(between.group(2))
        greater = re.search(r">\s*([\d\.]+)", range_part)
        if greater:
            return float(greater.group(1)), None
        less = re.search(r"<\s*([\d\.]+)", range_part)
        if less:
            return None, float(less.group(1))
        return None, None

    @classmethod
    def parse_biomarkers(cls, text: str, sex: Optional[str] = None) -> List[BiomarkerRow]:
        biomarkers: List[BiomarkerRow] = []
        lines = [ln for ln in text.splitlines() if ln.strip()]
        pattern = re.compile(
            r"(?P<name>[A-Za-z0-9\s\/%]+)\s+(?P<value>[\d\.]+)\s*(?P<unit>[A-Za-z\/\%]+)?\s*(?P<range><\s*[\d\.]+|>\s*[\d\.]+|[\d\.]+\s*[\-–]\s*[\d\.]+)?",
            re.IGNORECASE,
        )
        for line in lines:
            match = pattern.search(line)
            if not match:
                continue
            raw_name = match.group("name").strip()
            _, norm_name = cls._normalize_name(raw_name)
            value = float(match.group("value"))
            unit = (match.group("unit") or "").strip() or "units"
            ref_low, ref_high = cls._parse_range(match.group("range") or "")
            if ref_low is None and ref_high is None:
                ref_table = REFERENCE_RANGES.get(norm_name)
                if ref_table:
                    ref_low, ref_high = ref_table.get(sex or "any") or ref_table.get("any", (None, None))
            status = cls.compute_status(value, ref_low, ref_high)
            biomarkers.append(
                BiomarkerRow(
                    test_name_raw=raw_name,
                    test_name_norm=norm_name,
                    value=value,
                    unit=unit,
                    ref_low=ref_low,
                    ref_high=ref_high,
                    status=status,
                )
            )
        return biomarkers

    @staticmethod
    def compute_status(value: float, ref_low: Optional[float], ref_high: Optional[float]) -> str:
        if ref_low is not None and value < ref_low:
            return "LOW"
        if ref_high is not None and value > ref_high:
            return "HIGH"
        return "NORMAL"

    @staticmethod
    def identity_mismatch_score(profile_name: str, profile_sex: Optional[str], identity: Identity) -> float:
        score = 0.0
        if identity.patient_name:
            similarity = fuzz.partial_ratio(profile_name.lower(), identity.patient_name.lower()) / 100.0
            score += (1 - similarity) * 0.5
        if identity.sex and profile_sex:
            if identity.sex.lower()[0] != profile_sex.lower()[0]:
                score += 0.3
        if identity.age:
            score += min(abs(identity.age - 30) / 100, 0.2)  # simplistic placeholder
        return score


parser = ReportParser()
