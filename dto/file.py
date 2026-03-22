from pydantic import BaseModel


class File(BaseModel):
    """file data transfer object."""

    file_path: str
    file_extension: str