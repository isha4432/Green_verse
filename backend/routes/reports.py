from fastapi import APIRouter, Body
from fastapi.responses import Response
from typing import Dict, Any
from services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["Reports & PDF"])

@router.post("/pdf")
@router.post("/generate")
async def generate_pdf(report_data: Dict[str, Any] = Body(...)):
    pdf_buffer = ReportService.generate_pdf_report(report_data)
    pdf_bytes = pdf_buffer.getvalue()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=greenverse_climate_report.pdf"
        }
    )
