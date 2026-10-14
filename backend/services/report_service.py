import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportService:
    @staticmethod
    def generate_pdf_report(data: dict) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom typography styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#2C5E3A')
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#5B6052')
        )

        h2_style = ParagraphStyle(
            'ReportH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#22261E'),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#22261E')
        )

        elements = []

        # Title & Header
        title_text = data.get("title", "Green Verse Agronomic & Climate Assessment Report")
        elements.append(Paragraph(title_text, title_style))
        gen_time = datetime.now().strftime("%d %B %Y · %H:%M UTC")
        elements.append(Paragraph(f"Generated: {gen_time} | Platform: Green Verse Quantum–AI Agriculture", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2C5E3A'), spaceBefore=4, spaceAfter=14))

        # Executive Summary
        elements.append(Paragraph("Executive Summary", h2_style))
        summary_txt = data.get("summary", "This report contains simulated scenarios, quantum-classical irrigation optimizations, and soil-water management records.")
        elements.append(Paragraph(summary_txt, body_style))
        elements.append(Spacer(1, 12))

        # KPIs Summary Table
        kpis = data.get("kpis", [
            {"label": "Farm Area", "value": "2.4 ha"},
            {"label": "Water Budget", "value": "45.0 kL"},
            {"label": "Average Moisture", "value": "52.4 %"},
            {"label": "Climate Risk Score", "value": "28 / 100 (Good)"}
        ])

        kpi_data = [["Metric", "Value"]]
        for k in kpis:
            kpi_data.append([str(k.get("label", "")), str(k.get("value", ""))])

        t_kpi = Table(kpi_data, colWidths=[240, 280])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5E3A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FDFCF7'), colors.HexColor('#EDE7D7')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D5CCB2'))
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 14))

        # Experiments & Optimizations
        experiments = data.get("experiments", [])
        if experiments:
            elements.append(Paragraph("Recent Experiments & Quantum Allocations", h2_style))
            exp_rows = [["ID", "Name", "Type", "Status", "Date"]]
            for exp in experiments[:8]:
                exp_rows.append([
                    str(exp.get("id", "—")),
                    str(exp.get("name", "—"))[:32],
                    str(exp.get("type", "—")),
                    str(exp.get("status", "—")),
                    str(exp.get("date", "—"))
                ])
            t_exp = Table(exp_rows, colWidths=[65, 175, 95, 110, 75])
            t_exp.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#33739E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FDFCF7'), colors.HexColor('#EDE7D7')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D5CCB2'))
            ]))
            elements.append(t_exp)
            elements.append(Spacer(1, 14))

        # Notes / Disclaimer
        elements.append(Paragraph("System Notes & Disclaimers", h2_style))
        disclaimer = (
            "Green Verse is a decision-support prototype integrating simulated AI crop vulnerability inference "
            "and Qiskit Aer QAOA / Classical mathematical solvers. Optimization benchmarks reflect statevector simulations."
        )
        elements.append(Paragraph(disclaimer, body_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
