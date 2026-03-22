from pydantic import BaseModel


class Summary(BaseModel):
    """file data transfer object."""

    file_path: str
    summary_text: str