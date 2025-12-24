import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ..models import Profile, Report, Biomarker


def generate_sbar_pdf(profile: Profile, report: Report, biomarkers: list[Biomarker]) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    def write(line: str, spacer: int = 18):
        nonlocal y
        c.drawString(40, y, line)
        y -= spacer

    write("Blood Report SBAR Summary", 22)
    write(f"Profile: {profile.name} | Sex: {profile.sex or 'N/A'} | DOB: {profile.dob or 'N/A'}")
    write(f"Conditions: {', '.join(profile.conditions or []) or 'None'}")
    write(f"Meds: {', '.join(profile.meds or []) or 'None'}")
    write(" ")

    write("Situation (S): Top findings")
    abnormal = [b for b in biomarkers if b.status in {"HIGH", "LOW"}]
    for b in abnormal[:3]:
        write(f"- {b.test_name_norm}: {b.value_float} {b.unit} (ref {b.ref_low}-{b.ref_high})")
    if not abnormal:
        write("- No critical abnormalities detected in this summary.")
    write(" ")

    write("Background (B):")
    write(f"Report date: {report.report_date or report.created_at.date()}")
    write("Last report: See history in app if available.")
    write(" ")

    write("Assessment (A):")
    for b in abnormal:
        write(f"- {b.test_name_norm} {b.status.lower()} vs ref")
    if not abnormal:
        write("- Values within reference for monitored items.")
    write(" ")

    write("Recommendation (R):")
    write("- Discuss flagged items with a clinician; bring symptoms and medication list.")
    write("- Consider retest as advised or within 3-6 months depending on context.")
    write(" ")

    c.setFont("Helvetica", 8)
    write("This summary is educational decision-support and not a diagnosis. Please consult a qualified clinician.", 14)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
