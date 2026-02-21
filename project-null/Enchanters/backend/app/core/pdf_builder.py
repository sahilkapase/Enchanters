import io
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import logging

logger = logging.getLogger(__name__)


def build_scheme_form_pdf(
    farmer_data: dict,
    scheme_data: dict,
    generated_by: str = "farmer",
    agent_name: str | None = None,
) -> tuple[bytes, str]:
    """Generate a pre-filled scheme application form PDF. Returns (pdf_bytes, filename)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=16, spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Heading2"], alignment=TA_CENTER, fontSize=12, spaceAfter=8
    )
    normal_style = styles["Normal"]
    bold_style = ParagraphStyle("BoldStyle", parent=normal_style, fontName="Helvetica-Bold")

    elements = []

    elements.append(Paragraph("KisaanSeva - Government Scheme Application", title_style))
    elements.append(Paragraph(f"Scheme: {scheme_data.get('name_en', 'N/A')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", normal_style))
    elements.append(Paragraph(f"Application Reference: KS-{uuid.uuid4().hex[:8].upper()}", normal_style))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("APPLICANT DETAILS", bold_style))
    elements.append(Spacer(1, 0.3 * cm))

    farmer_table_data = [
        ["Farmer ID", farmer_data.get("farmer_id", "N/A")],
        ["Name", farmer_data.get("name", "N/A")],
        ["Phone", farmer_data.get("phone", "N/A")],
        ["District", farmer_data.get("district", "N/A")],
        ["State", farmer_data.get("state", "N/A")],
        ["PIN Code", farmer_data.get("pin_code", "N/A")],
        ["Land Area", f"{farmer_data.get('land_area', 'N/A')} {farmer_data.get('land_unit', 'acre')}"],
    ]

    if farmer_data.get("aadhaar_masked"):
        farmer_table_data.append(["Aadhaar (masked)", f"XXXX-XXXX-{farmer_data['aadhaar_masked']}"])
    if farmer_data.get("bank_ifsc"):
        farmer_table_data.append(["Bank IFSC", farmer_data["bank_ifsc"]])
    if farmer_data.get("ownership_type"):
        farmer_table_data.append(["Ownership", farmer_data["ownership_type"]])
    if farmer_data.get("irrigation_type"):
        farmer_table_data.append(["Irrigation", farmer_data["irrigation_type"]])

    table = Table(farmer_table_data, colWidths=[5 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.Color(0.9, 0.95, 0.9)),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))

    if farmer_data.get("crops"):
        elements.append(Paragraph("CROPS", bold_style))
        elements.append(Spacer(1, 0.3 * cm))
        crop_rows = [["Crop", "Season", "Year"]]
        for crop in farmer_data["crops"]:
            crop_rows.append([
                crop.get("crop_name", "N/A"),
                crop.get("season", "N/A"),
                str(crop.get("year", "N/A")),
            ])
        crop_table = Table(crop_rows, colWidths=[5 * cm, 5 * cm, 5 * cm])
        crop_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.2, 0.5, 0.2)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(crop_table)
        elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("SCHEME DETAILS", bold_style))
    elements.append(Spacer(1, 0.3 * cm))
    scheme_info = [
        ["Scheme Name", scheme_data.get("name_en", "N/A")],
        ["Ministry", scheme_data.get("ministry", "N/A")],
        ["Benefit Type", scheme_data.get("benefit_type", "N/A")],
        ["Benefit Amount", scheme_data.get("benefit_amount", "N/A")],
    ]
    scheme_table = Table(scheme_info, colWidths=[5 * cm, 10 * cm])
    scheme_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.Color(0.9, 0.9, 0.95)),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(scheme_table)
    elements.append(Spacer(1, 0.5 * cm))

    docs_required = scheme_data.get("documents_required", [])
    if docs_required:
        elements.append(Paragraph("DOCUMENTS REQUIRED", bold_style))
        elements.append(Spacer(1, 0.3 * cm))
        for doc in docs_required:
            elements.append(Paragraph(f"☐  {doc.replace('_', ' ').title()}", normal_style))
        elements.append(Spacer(1, 0.5 * cm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 0.3 * cm))

    if generated_by == "agent" and agent_name:
        elements.append(Paragraph(f"Generated by Agent: {agent_name}", normal_style))

    elements.append(Paragraph("Applicant Signature: ____________________", normal_style))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(
        "This form was auto-generated by KisaanSeva platform. "
        "Please verify all details before submission.",
        ParagraphStyle("Disclaimer", parent=normal_style, fontSize=8, textColor=colors.grey),
    ))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    scheme_slug = scheme_data.get("name_en", "scheme").replace(" ", "_")[:30]
    filename = f"{farmer_data.get('farmer_id', 'farmer')}_{scheme_slug}_{datetime.now().strftime('%Y%m%d')}.pdf"

    logger.info("Generated PDF form: %s (%d bytes)", filename, len(pdf_bytes))
    return pdf_bytes, filename


def build_insurance_form_pdf(farmer_data: dict, plan_data: dict) -> tuple[bytes, str]:
    """Generate a pre-filled insurance enrollment form PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=16, spaceAfter=12)
    normal_style = styles["Normal"]
    bold_style = ParagraphStyle("Bold2", parent=normal_style, fontName="Helvetica-Bold")

    elements = []
    elements.append(Paragraph("KisaanSeva - Insurance Enrollment Form", title_style))
    elements.append(Paragraph(f"Plan: {plan_data.get('name_en', 'N/A')}", ParagraphStyle("Sub", parent=styles["Heading2"], alignment=TA_CENTER)))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", normal_style))
    elements.append(Spacer(1, 0.5 * cm))

    info = [
        ["Farmer ID", farmer_data.get("farmer_id", "N/A")],
        ["Name", farmer_data.get("name", "N/A")],
        ["Phone", farmer_data.get("phone", "N/A")],
        ["District", farmer_data.get("district", "N/A")],
        ["State", farmer_data.get("state", "N/A")],
        ["Land Area", f"{farmer_data.get('land_area', 'N/A')} {farmer_data.get('land_unit', 'acre')}"],
        ["Plan Type", plan_data.get("plan_type", "N/A")],
    ]
    table = Table(info, colWidths=[5 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.Color(0.9, 0.95, 0.9)),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph("Applicant Signature: ____________________", normal_style))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    filename = f"{farmer_data.get('farmer_id', 'farmer')}_insurance_{plan_data.get('plan_type', 'plan')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return pdf_bytes, filename
