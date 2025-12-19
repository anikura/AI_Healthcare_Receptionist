import logging
import io
import re
from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def setup_logging(log_file, level):
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
    )

def format_phone_display(phone):
    if phone and len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    return phone

def format_date_display(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%B %d, %Y")
    except:
        return date_str

def format_time_display(time_str):
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%I:%M %p").lstrip("0")
    except:
        return time_str

def clean_text_for_tts(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"[^\w\s,.!?]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def generate_pdf_receipt(data: Dict, title: str):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 22)
    pdf.setFillColor(colors.darkblue)
    pdf.drawString(50, height - 50, "XYZ Hospital")

    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(colors.black)
    pdf.drawString(50, height - 70, "123 Health Street, New Delhi")
    pdf.drawString(50, height - 85, "+91-1234567890")

    pdf.line(50, height - 100, width - 50, height - 100)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 140, title)

    y = height - 180
    for key, value in data.items():
        label = key.replace("_", " ").title()
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(50, y, f"{label}:")
        pdf.setFont("Helvetica", 11)
        text = str(value)
        if len(text) > 70:
            pdf.drawString(200, y, text[:70])
            y -= 15
            pdf.drawString(200, y, text[70:140])
        else:
            pdf.drawString(200, y, text)
        y -= 25

    pdf.line(50, 100, width - 50, 100)
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(50, 80, f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    pdf.drawString(50, 65, "This is a system generated document")

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
