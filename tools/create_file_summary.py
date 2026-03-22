from tools.client import get_client
from tools.prompt import get_prompt_from_file
from llm_instructions import LLM_INSTRUCTION_DIRECTORY
from pathlib import Path
import base64
from dto.slide import Slide
from database.database_operations import (
    insert_to_slide_table,
)

client = get_client()
async def summarize_slide(slide_path:Path)->None:
    """Summary slide content.
    
    :param slide_path: path to individual slide.
    :return: slide summary.
    """

    with open(slide_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    instruction_file_path = LLM_INSTRUCTION_DIRECTORY / "slide_summary.yaml"
    system_prompt = get_prompt_from_file(
        file_path=instruction_file_path,
        prompt_type="system",
    )
    user_prompt = get_prompt_from_file(
        file_path=instruction_file_path,
        prompt_type="user",
    )

    response  = client.chat.completions.create( #type:ignore
        model =  "gpt-4o",
        messages = [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user", 
                            "content": [
                                        {
                                        "type": "text", 
                                        "text": user_prompt
                                        },
                                        {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                                        }
                                        ]
                    
                        }
                    ]
        )
    slide_summary =  response.choices[0].message.content or "test"

    await insert_to_slide_table(
            data = Slide(
            file_id = 2,
            slide_path = str(slide_path),
            slide_summary = slide_summary,
            running_summary="test"
            )
        )