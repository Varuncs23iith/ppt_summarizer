import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from tools.extract_metadata import process_file
from tools.prepare_config import config
from tools.create_file_summary import summarize_all_slides
import asyncio

test_file = Path("data/FedEVI_FL.pptx")

async def main():
    """Generate slide analysis."""
    print(f"Processing: {test_file}")

    file_id, pdf_path, output_dir = await process_file(test_file, config)
    await summarize_all_slides(pdf_path, file_id, output_dir)

    print(f"\n✓ Completed for file_id={file_id}")


if __name__ == "__main__":
    asyncio.run(main())
