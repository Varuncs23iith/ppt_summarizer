from enum import StrEnum, auto


class AllowedInputExtensions(StrEnum):
    """Allowed input extensions."""

    PPTX = ".pptx"
    PPT = ".ppt"
    PDF = ".pdf"
