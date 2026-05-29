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

async def process_file(file_path: Path, config: Box) -> tuple[int, Path, Path]:
    """Process pdf/ppt file.
    
    :param file_path: ppt/pdf file to process.
    :param config: configuration file.
    :return: Tuple of (file_id, pdf_path, output_dir)
    """
    extension = file_path.suffix
    output_dir = Path(config.ppt_to_pdf_conversion.out_dir)
    
    if extension in [AllowedInputExtensions.PPT, AllowedInputExtensions.PPTX]:
        # Convert PPT/PPTX to PDF
        ppt_to_pdf_from_path(file_path, config)
        pdf_path = output_dir / f"{file_path.stem}.pdf"
        
        # Insert to database and get file_id
        file_id = await insert_to_file_table(
            data=File(file_path=str(pdf_path), file_extension="pdf")
        )
        
        # Convert PDF to images
        pdf_to_images(pdf_path, config)
        
    elif extension == AllowedInputExtensions.PDF:
        # Insert PDF to database and get file_id
        file_id = await insert_to_file_table(
            data=File(file_path=str(file_path), file_extension="pdf")
        )
        pdf_path = file_path
        
        # Convert PDF to images
        pdf_to_images(file_path, config)
        
    else:
        raise ValueError(f"File format not supported: {extension}")
    
    return file_id, pdf_path, output_dir


def pil_to_base64(img: Image.Image) -> str:
    """Convert a PIL Image to a base64 encoded PNG string.

    :param img: input image to convert to base64 format.
    :return: base64 encoded image.
    """
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def ppt_to_pdf_from_path(file_path: Path, config: Box) -> None:
    """Convert ppt/pptx files to pdf.
    
    :param file_path: ppt file to convert to pdf.
    :param config: configuration file.
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


def pdf_to_images(file_path: Path, config: Box) -> None:
    """Convert pdf to images.
    
    :param file_path: pdf file to convert to images.
    :param config: configuration file.
    """
    images = convert_from_path(file_path, dpi=200)
    output_dir = Path(config.ppt_to_pdf_conversion.out_dir)
    
    for i, image in enumerate(images, start=1):
        img_path = output_dir / f"{file_path.stem}_page_{i}.png"
        image.save(img_path)
