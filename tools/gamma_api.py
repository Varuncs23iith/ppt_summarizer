"""
Gamma API integration for generating presentations from analyzed slides.
"""

import re
import asyncio
import httpx
from database.database_operations import get_slides_by_file_id, get_improvement_by_slide_id
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_gamma_api_key() -> str:
    """Get Gamma API key."""
    api_key = os.environ.get("GAMMA_API_KEY") or os.getenv("GAMMA_API_KEY")
    if not api_key:
        raise ValueError(
            "GAMMA_API_KEY not found. Please set it in .env file or environment variables."
        )
    return api_key


def extract_gamma_instructions(improvement_points: str) -> str:
    """Extract GAMMA INSTRUCTIONS section from improvement points."""
    match = re.search(
        r'GAMMA INSTRUCTIONS:\s*(.+?)(?=\n\n|\Z)',
        improvement_points,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        return match.group(1).strip()
    return ""


def format_slide_for_gamma(slide_transcription: str, slide_summary: str, improvement_points: str) -> str:
    """Format slide data into Gamma-compatible markdown."""
    gamma_instructions = extract_gamma_instructions(improvement_points)

    formatted = []

    if slide_summary:
        formatted.append(f"<!-- Summary: {slide_summary} -->")
        formatted.append("")

    formatted.append(slide_transcription)

    if gamma_instructions:
        formatted.append("")
        formatted.append(f"<!-- Gamma Instructions: {gamma_instructions} -->")

    return "\n".join(formatted)


async def create_presentation(aggregated_markdown: str, api_key: str, num_slides: int) -> str:
    """Call Gamma API to create presentation."""
    url = "https://public-api.gamma.app/v1.0/generations"
    headers = {"Content-Type": "application/json", "X-API-KEY": api_key}
    payload = {
        "inputText": aggregated_markdown,
        "textMode": "preserve",
        "format": "presentation",
        "exportAs": "pptx",
        "numCards": num_slides
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=30.0)
        result = response.json()
        return result.get("generationId")


async def poll_generation_status(generation_id: str, api_key: str) -> dict:
    """Poll Gamma API until generation completes."""
    url = f"https://public-api.gamma.app/v1.0/generations/{generation_id}"
    headers = {"X-API-KEY": api_key}

    async with httpx.AsyncClient() as client:
        for _ in range(120):  # 10 minutes max
            response = await client.get(url, headers=headers, timeout=15.0)
            status_data = response.json()

            if status_data.get("status") == "completed":
                return {
                    "gammaUrl": status_data.get("gammaUrl"),
                    "exportUrl": status_data.get("exportUrl")
                }

            await asyncio.sleep(5)


async def generate_presentation_from_file(file_id: int) -> dict:
    """
    Generate Gamma presentation from slides in database.

    :param file_id: File ID from database
    :return: Dictionary with gammaUrl and exportUrl
    """
    api_key = get_gamma_api_key()

    # Fetch slides
    slides = await get_slides_by_file_id(file_id)
    num_slides = len(slides)

    # Format each slide
    formatted_slides = []
    for slide in slides:
        improvement = await get_improvement_by_slide_id(slide.slide_id)
        improvement_points = improvement.improvement_points if improvement else ""

        formatted_slide = format_slide_for_gamma(
            slide_transcription=slide.slide_transcription,
            slide_summary=slide.slide_summary,
            improvement_points=improvement_points
        )
        formatted_slides.append(formatted_slide)

    # Combine and send to Gamma
    aggregated_markdown = "\n\n/split\n\n".join(formatted_slides)
    generation_id = await create_presentation(aggregated_markdown, api_key, num_slides)
    result = await poll_generation_status(generation_id, api_key)

    return result
