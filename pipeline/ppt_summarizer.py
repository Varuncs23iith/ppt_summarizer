import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from pathlib import Path
from tools.extract_metadata import process_file
from tools.prepare_config import config
from tools.create_file_summary import summarize_slide
import asyncio

test_file = Path("data/CV_accelarator.pptx")
slide_path = Path("data/CV_accelarator_page_1.png")

async def main():
    await process_file(test_file, config)
    await summarize_slide(slide_path)

if __name__ == "__main__":
    asyncio.run(main())



