from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

def format_datetime(dt):
    # Check if the object is a datetime instance and format it
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')  # You can adjust the format as needed
    return str(dt)

def format_status(status):
    if status == 2:
        return "Failed"
    elif status == 3:
        return "Success"
    else:
        return str(status)  # Or handle other statuses as needed

def create_pdf(data_list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    # Styles for the document
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    styleN.fontSize = 5  # Reduce font size

    # Create a list to hold the elements for the PDF
    elements = []

    # Add a title
    elements.append(Paragraph('Genie AI Usage Report', styleH))

    # Define column headers
    headers = ['DateTime', 'Resource Name', 'AI Engine', 'Total Tokens', 'Total Cost', 'Total Time', 'Status']

    # Convert headers and data to Paragraphs
    formatted_headers = [Paragraph('<b>{}</b>'.format(h), styleN) for h in headers]
    formatted_data = [[
        Paragraph(format_datetime(row['datetime']), styleN),
        Paragraph(str(row['resourcename']), styleN),
        Paragraph(str(row['ai_engine']), styleN),
        Paragraph(str(row['total_tokens']), styleN),
        Paragraph(str(row['total_cost']), styleN),
        Paragraph(str(row['total_time']), styleN),
        Paragraph(format_status(row['status']), styleN)
    ] for row in data_list]

    # Prepare data with headers
    data = [formatted_headers] + formatted_data

    # Set column widths
    # col_widths = [100, 150, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]  # Adjust as needed

    # Create a table and style it
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    t.splitByRow = True  # Allow table to split across pages

    elements.append(t)

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
