from tools.client import get_client
from tools.prompt import get_prompt_from_file
from llm_instructions import LLM_INSTRUCTION_DIRECTORY
from pathlib import Path
import base64
from dto.slide import Slide
from dto.slide_improvement import SlideImprovement
from database.database_operations import (
    insert_to_slide_table,
    insert_to_improvement_table
)
import re
from database.database_operations import get_slides_by_file_id

client = get_client()


def parse_combined_response(response_text: str) -> dict:
    """Parse the combined response into four parts."""
    
    parts = {
        'slide_transcription': '',
        'slide_summary': '',
        'running_summary': '',
        'improvements': ''
    }
    
    # Split by section markers
    sections = response_text.split('=== ')
    
    for section in sections:
        if section.startswith('SLIDE TRANSCRIPTION ==='):
            parts['slide_transcription'] = section.replace('SLIDE TRANSCRIPTION ===', '').strip()
        elif section.startswith('SLIDE SUMMARY ==='):
            parts['slide_summary'] = section.replace('SLIDE SUMMARY ===', '').strip()
        elif section.startswith('RUNNING SUMMARY ==='):
            parts['running_summary'] = section.replace('RUNNING SUMMARY ===', '').strip()
        elif section.startswith('IMPROVEMENTS ==='):
            parts['improvements'] = section.replace('IMPROVEMENTS ===', '').strip()
    
    return parts


def extract_scores(improvements_text: str) -> dict:
    """Extract scores from improvements section."""
    scores = {}
    
    # Extract scores
    patterns = {
        'content_clarity_score': r'Content Clarity:\s*(\d+(?:\.\d+)?)',
        'visual_design_score': r'Visual Design:\s*(\d+(?:\.\d+)?)',
        'information_density_score': r'Information Density:\s*(\d+(?:\.\d+)?)',
        'engagement_score': r'Engagement:\s*(\d+(?:\.\d+)?)',
        'overall_score': r'Overall:\s*(\d+(?:\.\d+)?)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, improvements_text, re.IGNORECASE)
        if match:
            scores[key] = float(match.group(1))
        else:
            scores[key] = 0.0
    
    return scores


async def analyze_slide(
    slide_path: Path, 
    file_id: int, 
    slide_number: int,
    total_slides: int,
    previous_running_summary: str = ""
) -> tuple[str, str, str, str]:
    """Analyze slide and return transcription, summary, running summary, and suggestions.
    
    :param slide_path: Path to slide image
    :param file_id: File ID from database
    :param slide_number: Current slide number
    :param total_slides: Total number of slides
    :param previous_running_summary: Previous cumulative summary
    :return: (slide_transcription, slide_summary, running_summary, improvements_text)
    """
    
    with open(slide_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    
    # Load combined instruction
    instruction_file_path = LLM_INSTRUCTION_DIRECTORY / "slide_analysis.yaml"
    system_prompt = get_prompt_from_file(
        file_path=instruction_file_path,
        prompt_type="system",
    )
    user_prompt = get_prompt_from_file(
        file_path=instruction_file_path,
        prompt_type="user",
    )
    
    # Format user prompt
    formatted_user_prompt = user_prompt.format(
        slide_number=slide_number,
        total_slides=total_slides,
        previous_running_summary=previous_running_summary if previous_running_summary else "This is the first slide."
    )
    
    # ONE LLM call to get everything
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": formatted_user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ]
    )
    
    full_response = response.choices[0].message.content or ""
    
    # Parse response into four parts
    parts = parse_combined_response(full_response)
    
    slide_transcription = parts['slide_transcription']
    slide_summary = parts['slide_summary']
    running_summary = parts['running_summary']
    improvements_text = parts['improvements']
    
    # Extract scores from improvements
    scores = extract_scores(improvements_text)
    
    # Store slide transcription, summary and running summary
    await insert_to_slide_table(
        data=Slide(
            file_id=file_id,
            slide_path=str(slide_path),
            slide_transcription=slide_transcription,
            slide_summary=slide_summary,
            running_summary=running_summary
        )
    )
    

    slides = await get_slides_by_file_id(file_id)
    current_slide = slides[-1]  # Last inserted slide
    
    # Store improvements
    await insert_to_improvement_table(
        data=SlideImprovement(
            slide_id=current_slide.slide_id,
            content_clarity_score=scores.get('content_clarity_score', 0.0),
            visual_design_score=scores.get('visual_design_score', 0.0),
            information_density_score=scores.get('information_density_score', 0.0),
            engagement_score=scores.get('engagement_score', 0.0),
            overall_score=scores.get('overall_score', 0.0),
            improvement_points=improvements_text
        )
    )
    
    return slide_transcription, slide_summary, running_summary, improvements_text


async def summarize_all_slides(pdf_path: Path, file_id: int, output_dir: Path) -> None:
    """Analyze all slides - each call generates transcription, summary, running summary, AND improvements."""
    
    pdf_stem = pdf_path.stem
    slide_images = sorted(output_dir.glob(f"{pdf_stem}_page_*.png"))
    
    if not slide_images:
        print(f"No slide images found for {pdf_stem}")
        return
    
    total_slides = len(slide_images)
    
    running_summary = ""
    for idx, slide_path in enumerate(slide_images, start=1):
        print(f"{idx}/{total_slides} Analyzing Slide {idx}")
        
        slide_transcription, slide_summary, running_summary, improvements = await analyze_slide(
            slide_path=slide_path,
            file_id=file_id,
            slide_number=idx,
            total_slides=total_slides,
            previous_running_summary=running_summary
        )
