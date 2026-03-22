from pydantic import BaseModel


class Slide(BaseModel):
    """file data transfer object."""

    file_id: int
    slide_path: str
    slide_summary: str
    running_summary: str