from typing import List, Optional
from .parser import BiomarkerRow

EXPLANATIONS = {
    "hba1c": "HbA1c reflects average glucose control over the past ~3 months.",
    "hemoglobin": "Hemoglobin carries oxygen in red blood cells and can be affected by nutrition or bleeding.",
    "wbc": "White blood cells are part of immune response and can be associated with infection or inflammation.",
}

LIFESTYLE_TIPS = {
    "hba1c": ["Aim for balanced meals with fiber and protein.", "Stay active most days of the week."],
    "ldl": ["Emphasize whole grains and vegetables.", "Limit saturated fats and trans fats."],
    "hdl": ["Regular movement can support HDL levels.", "Discuss exercise plans with your clinician."],
    "hemoglobin": ["Ensure adequate iron-rich foods if appropriate.", "Stay hydrated."],
}

RED_FLAGS = {
    "hba1c": ["Very high glucose can be associated with diabetes; discuss urgently if symptomatic."],
    "hemoglobin": ["Very low hemoglobin can be associated with anemia; seek care if dizzy or short of breath."],
}


def build_insights(rows: List[BiomarkerRow], previous_rows: Optional[List[BiomarkerRow]] = None):
    insights = []
    previous_map = {row.test_name_norm: row for row in (previous_rows or [])}
    urgent_flags = []
    key_abnormalities = []

    for row in rows:
        prev = previous_map.get(row.test_name_norm)
        comparison = _compare(prev, row) if prev else {
            "prev_value": None,
            "delta": None,
            "pct_change": None,
            "trend": None,
        }
        explanation = EXPLANATIONS.get(row.test_name_norm, "This biomarker is provided for educational review.")
        lifestyle = LIFESTYLE_TIPS.get(row.test_name_norm, ["Maintain a balanced diet and regular activity as advised."])
        red_flags = RED_FLAGS.get(row.test_name_norm, [])
        if row.status in {"HIGH", "LOW"}:
            key_abnormalities.append(row.test_name_norm)
            if row.status == "HIGH":
                urgent_flags.extend([f"{row.test_name_norm} elevated; discuss with a clinician if symptomatic."])
            if row.status == "LOW":
                urgent_flags.extend([f"{row.test_name_norm} lower than typical; discuss with a clinician if you feel unwell."])
        insights.append(
            {
                "test_name": row.test_name_norm,
                "standard_code": None,
                "value": row.value,
                "unit": row.unit,
                "ref_low": row.ref_low,
                "ref_high": row.ref_high,
                "status": row.status,
                "explanation": explanation,
                "lifestyle_tips": lifestyle,
                "red_flags": red_flags,
                "compare_to_previous": comparison,
            }
        )

    return {
        "biomarkers": insights,
        "overall_summary": {
            "key_abnormalities": key_abnormalities,
            "urgent_flags": urgent_flags,
        },
        "disclaimers": [
            "This is educational decision-support and not medical advice.",
            "Please discuss all results with a qualified clinician.",
        ],
    }


def _compare(prev: BiomarkerRow, current: BiomarkerRow):
    delta = current.value - prev.value
    pct_change = (delta / prev.value * 100) if prev.value else None
    trend = "IMPROVING"
    if delta > 0:
        trend = "WORSENING"
    if abs(delta) < 0.01:
        trend = "STABLE"
    return {
        "prev_value": prev.value,
        "delta": delta,
        "pct_change": pct_change,
        "trend": trend,
    }
