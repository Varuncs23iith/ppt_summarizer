"""
API Controller for PPT Summarizer

Provides two main endpoints:
1. /summarize - Analyze presentation and return PDF summary
2. /generate-gamma - Create Gamma presentation and return download link
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import asyncio
from datetime import datetime
import tempfile
import shutil
from typing import Optional

from tools.extract_metadata import process_file
from tools.prepare_config import config
from tools.create_file_summary import summarize_all_slides
from tools.gamma_api import generate_presentation_from_file
from database.database_operations import get_slides_by_file_id, get_improvement_by_slide_id

# PDF generation imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT


app = FastAPI(
    title="PPT Summarizer API",
    description="AI-powered presentation analysis and Gamma deck generation",
    version="1.0.0"
)


class SummarizeRequest(BaseModel):
    """Request model for summarize endpoint."""
    file_path: str


class SummarizeResponse(BaseModel):
    """Response model for summarize endpoint."""
    file_id: int
    pdf_path: str
    suggestions_pdf_path: str
    total_slides: int
    message: str


class GammaDeckRequest(BaseModel):
    """Request model for gamma deck generation."""
    file_id: int


class GammaDeckResponse(BaseModel):
    """Response model for gamma deck generation."""
    file_id: int
    gamma_url: str
    export_url: str
    message: str


def process_text_for_pdf(text: str) -> str:
    """
    Process text to handle mathematical equations and special formatting for PDF.

    Converts LaTeX-style equations to readable text and handles special characters.
    """
    import re

    # Remove LaTeX delimiters
    text = text.replace('\\[', '')
    text = text.replace('\\]', '')
    text = text.replace('$$', '')
    text = text.replace('$', '')
    text = text.replace('\\(', '')
    text = text.replace('\\)', '')

    # Convert common LaTeX commands to readable text
    text = text.replace('\\frac{', '(')
    text = text.replace('}{', ')/(')
    text = text.replace('\\alpha', 'α')
    text = text.replace('\\beta', 'β')
    text = text.replace('\\gamma', 'γ')
    text = text.replace('\\delta', 'δ')
    text = text.replace('\\theta', 'θ')
    text = text.replace('\\lambda', 'λ')
    text = text.replace('\\mu', 'μ')
    text = text.replace('\\sigma', 'σ')
    text = text.replace('\\pi', 'π')
    text = text.replace('\\sum', 'Σ')
    text = text.replace('\\prod', 'Π')
    text = text.replace('\\infty', '∞')
    text = text.replace('\\leq', '≤')
    text = text.replace('\\geq', '≥')
    text = text.replace('\\neq', '≠')
    text = text.replace('\\times', '×')
    text = text.replace('\\div', '÷')
    text = text.replace('\\approx', '≈')
    text = text.replace('\\pm', '±')
    text = text.replace('\\sqrt', '√')

    # Remove remaining backslashes
    text = text.replace('\\', '')

    # Handle subscripts and superscripts
    # Handle {...} for subscripts and superscripts first
    text = re.sub(r'\^{([^}]+)}', r'<super>\1</super>', text)  # ^{...}
    text = re.sub(r'_{([^}]+)}', r'<sub>\1</sub>', text)       # _{...}
    # Then handle single character subscripts/superscripts
    text = re.sub(r'\^(\w)', r'<super>\1</super>', text)       # ^x
    text = re.sub(r'_(\w)', r'<sub>\1</sub>', text)            # _x
    # Clean up remaining braces
    text = text.replace('{', '').replace('}', '')

    # Replace newlines with <br/> for proper rendering
    text = text.replace('\n', '<br/>')

    return text


async def generate_suggestions_pdf(file_id: int, slides_data: list, output_path: str) -> None:
    """
    Generate a PDF report with slide improvement suggestions.

    :param file_id: File ID from database
    :param slides_data: List of slide objects from database
    :param output_path: Path where PDF should be saved
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify',
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='SlideTitle',
        fontSize=14,
        leading=16,
        textColor='#2c3e50',
        spaceAfter=12,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=16,
        leading=18,
        textColor='#34495e',
        spaceAfter=20,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    ))

    # Add title page
    title_style = ParagraphStyle(
        name='Title',
        fontSize=24,
        leading=28,
        textColor='#2c3e50',
        spaceAfter=30,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )

    elements.append(Paragraph(f"Slide Improvement Suggestions", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"File ID: {file_id}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(f"Total Slides: {len(slides_data)}", styles['Normal']))
    elements.append(PageBreak())

    # Add each slide's suggestions on its own page
    for idx, slide in enumerate(slides_data, 1):
        # Slide header
        elements.append(Paragraph(f"Slide {idx} - Improvement Suggestions", styles['SectionTitle']))
        elements.append(Spacer(1, 0.1 * inch))

        # Get improvement suggestions
        improvement = await get_improvement_by_slide_id(slide.slide_id)
        suggestions_text = improvement.improvement_points if improvement else "No suggestions available"

        # Process mathematical equations and special formatting
        suggestions_text = process_text_for_pdf(suggestions_text)

        elements.append(Paragraph(suggestions_text, styles['Justify']))
        elements.append(Spacer(1, 0.3 * inch))

        # Add page break except for last slide
        if idx < len(slides_data):
            elements.append(PageBreak())

    # Build PDF
    doc.build(elements)


def generate_summary_pdf(file_id: int, slides_data: list, output_path: str) -> None:
    """
    Generate a PDF report with slide summaries.

    :param file_id: File ID from database
    :param slides_data: List of slide objects from database
    :param output_path: Path where PDF should be saved
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify',
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='SlideTitle',
        fontSize=14,
        leading=16,
        textColor='#2c3e50',
        spaceAfter=12,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=16,
        leading=18,
        textColor='#34495e',
        spaceAfter=20,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    ))

    # Add title page
    title_style = ParagraphStyle(
        name='Title',
        fontSize=24,
        leading=28,
        textColor='#2c3e50',
        spaceAfter=30,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )

    elements.append(Paragraph(f"Presentation Analysis Report", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"File ID: {file_id}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(f"Total Slides: {len(slides_data)}", styles['Normal']))
    elements.append(PageBreak())

    # Add each slide summary on its own page
    for idx, slide in enumerate(slides_data, 1):
        # Slide header
        elements.append(Paragraph(f"Slide {idx}", styles['SectionTitle']))
        elements.append(Spacer(1, 0.1 * inch))

        # Slide Summary section (detailed)
        summary_text = slide.slide_summary or "No summary available"

        # Process mathematical equations and special formatting using helper function
        summary_text = process_text_for_pdf(summary_text)

        elements.append(Paragraph(summary_text, styles['Justify']))
        elements.append(Spacer(1, 0.3 * inch))

        # Add page break except for last slide
        if idx < len(slides_data):
            elements.append(PageBreak())

    # Add overall summary page (Executive Summary)
    elements.append(PageBreak())

    # Executive Summary header
    exec_summary_style = ParagraphStyle(
        name='ExecutiveSummary',
        fontSize=20,
        leading=24,
        textColor='#1a1a1a',
        spaceAfter=30,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    elements.append(Paragraph("Executive Summary", exec_summary_style))
    elements.append(Spacer(1, 0.2 * inch))

    if slides_data:
        # Use the last running summary as overall summary (should be executive summary style)
        overall_summary = slides_data[-1].running_summary or "No overall summary available"

        # Process mathematical equations and special formatting using helper function
        overall_summary = process_text_for_pdf(overall_summary)

        elements.append(Paragraph(overall_summary, styles['Justify']))

    # Build PDF
    doc.build(elements)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "PPT Summarizer API",
        "version": "1.0.0"
    }


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_presentation(request: SummarizeRequest):
    """
    Endpoint 1: Analyze presentation and generate PDF summary.

    Takes a file path, processes the presentation, generates slide summaries,
    and returns a PDF where each page contains the summary of each slide and
    the last page contains the overall summary.

    :param request: SummarizeRequest with file_path
    :return: SummarizeResponse with file_id and PDF path
    """
    try:
        # Validate file path
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

        if file_path.suffix.lower() not in ['.ppt', '.pptx', '.pdf']:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Supported formats: .ppt, .pptx, .pdf"
            )

        # Process file and generate summaries
        print(f"Processing file: {file_path}")
        file_id, pdf_path, output_dir = await process_file(file_path, config)

        print(f"Analyzing slides for file_id={file_id}")
        await summarize_all_slides(pdf_path, file_id, output_dir)

        # Get all slides from database
        slides = await get_slides_by_file_id(file_id)

        if not slides:
            raise HTTPException(
                status_code=500,
                detail="No slides were processed from the presentation"
            )

        # Generate PDF summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_output_path = f"data/summary_report_{file_id}_{timestamp}.pdf"
        suggestions_pdf_path = f"data/suggestions_report_{file_id}_{timestamp}.pdf"

        print(f"Generating PDF reports: {pdf_output_path}, {suggestions_pdf_path}")
        generate_summary_pdf(file_id, slides, pdf_output_path)
        await generate_suggestions_pdf(file_id, slides, suggestions_pdf_path)

        return SummarizeResponse(
            file_id=file_id,
            pdf_path=pdf_output_path,
            suggestions_pdf_path=suggestions_pdf_path,
            total_slides=len(slides),
            message=f"Successfully analyzed {len(slides)} slides. PDF reports generated."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/summarize/download/{file_id}")
async def download_summary_pdf(file_id: int):
    """
    Download the generated PDF summary for a given file_id.

    :param file_id: The file ID from the database
    :return: PDF file response
    """
    try:
        # Find the most recent summary PDF for this file_id
        data_dir = Path("data")
        pdf_files = list(data_dir.glob(f"summary_report_{file_id}_*.pdf"))

        if not pdf_files:
            raise HTTPException(
                status_code=404,
                detail=f"No PDF summary found for file_id={file_id}"
            )

        # Get the most recent PDF
        latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)

        return FileResponse(
            path=str(latest_pdf),
            media_type='application/pdf',
            filename=f"summary_report_{file_id}.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading PDF: {str(e)}")


@app.get("/suggestions/download/{file_id}")
async def download_suggestions_pdf(file_id: int):
    """
    Download the generated PDF suggestions for a given file_id.

    :param file_id: The file ID from the database
    :return: PDF file response
    """
    try:
        # Find the most recent suggestions PDF for this file_id
        data_dir = Path("data")
        pdf_files = list(data_dir.glob(f"suggestions_report_{file_id}_*.pdf"))

        if not pdf_files:
            raise HTTPException(
                status_code=404,
                detail=f"No PDF suggestions found for file_id={file_id}"
            )

        # Get the most recent PDF
        latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)

        return FileResponse(
            path=str(latest_pdf),
            media_type='application/pdf',
            filename=f"suggestions_report_{file_id}.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading PDF: {str(e)}")


@app.post("/generate-gamma", response_model=GammaDeckResponse)
async def generate_gamma_deck(request: GammaDeckRequest):
    """
    Endpoint 2: Generate Gamma presentation and return download link.

    Takes a file_id (from previous /summarize call), generates a Gamma deck
    using the analyzed slides, and returns the Gamma URL and export URL.

    :param request: GammaDeckRequest with file_id
    :return: GammaDeckResponse with URLs
    """
    try:
        file_id = request.file_id

        # Verify file_id exists in database
        slides = await get_slides_by_file_id(file_id)
        if not slides:
            raise HTTPException(
                status_code=404,
                detail=f"No slides found for file_id={file_id}. Please run /summarize first."
            )

        print(f"Generating Gamma presentation for file_id={file_id}")
        result = await generate_presentation_from_file(file_id)

        return GammaDeckResponse(
            file_id=file_id,
            gamma_url=result['gammaUrl'],
            export_url=result['exportUrl'],
            message=f"Successfully generated Gamma presentation with {len(slides)} slides."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Gamma deck: {str(e)}")


@app.post("/upload-and-summarize")
async def upload_and_summarize(file: UploadFile = File(...)):
    """
    Convenience endpoint: Upload a file and get summary in one call.

    :param file: Uploaded presentation file
    :return: SummarizeResponse with file_id and PDF path
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.ppt', '.pptx', '.pdf']:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Supported formats: .ppt, .pptx, .pdf"
            )

        # Save uploaded file temporarily
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"uploaded_{timestamp}_{file.filename}"
        temp_path = Path("data") / temp_filename

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the uploaded file
        request = SummarizeRequest(file_path=str(temp_path))
        response = await summarize_presentation(request)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
