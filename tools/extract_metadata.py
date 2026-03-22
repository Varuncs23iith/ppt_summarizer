import base64
import io
from pathlib import Path
from PIL import Image
import shutil
import subprocess
from box import Box
from pdf2image import convert_from_path
from pipeline.constants import AllowedInputExtensions
from database.database_operations import (
    insert_to_file_table,
)
from dto.file import File
from dto.slide import Slide

async def process_file(file_path:Path, config:Box):
    """Process pdf/ppt file.
    :param file_path: ppt file to convert to pdf.
    :config: configuration file.

    """
    extension = file_path.suffix
    if extension in [AllowedInputExtensions.PPT, AllowedInputExtensions.PPTX]:
        ppt_to_pdf_from_path(file_path, config)
        output_dir = config.ppt_to_pdf_conversion.out_dir
        pdf_path = Path(output_dir) / f"{file_path.stem}.pdf"
        await insert_to_file_table(
            data= File(file_path=str(pdf_path),
                       file_extension="pdf")
        )
        pdf_to_images(pdf_path, config)
    elif extension == AllowedInputExtensions.PDF:
         await insert_to_file_table(
            data= File(file_path=str(file_path),
                       file_extension="pdf")
        )
         pdf_to_images(file_path, config)
    else:
         raise ValueError("File format not supported")

def pil_to_base64(img: Image.Image) -> str:
    """Convert a PIL Image to a base64 encoded PNG string.

    :param: img: input image to convert to base64 format.
    return: base64 encoded image.
    """
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def ppt_to_pdf_from_path(file_path:Path, config:Box)->None:
    """Convert ppt/pptx files to pdf.
    
    :param file_path: ppt file to convert to pdf.
    :config: configuration file.
    """
    output_dir = config.ppt_to_pdf_conversion.out_dir
    libra_location = shutil.which("soffice")
    if not libra_location:
        raise ValueError(
            "Please install libraoffice in your OS."
        )
    subprocess.run(
            [
                libra_location,
                "--headless",
                "--convert-to",
                "pdf",
                str(file_path),
                "--outdir",
                output_dir
            ],
            check=True,
        )

def pdf_to_images(
    file_path:Path,
    config: Box
    )-> None:
    """Convert pdf to images.
    :param file_path: ppt file to convert to pdf.
    :config: configuration file.
    """

    images = convert_from_path(file_path, dpi=200)
    output_dir = Path(config.ppt_to_pdf_conversion.out_dir)
    i=1
    for image in images:
        img_path = output_dir / f"{file_path.stem}_page_{i}.png"
        image.save(img_path)
        i+=1

