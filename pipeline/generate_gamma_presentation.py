"""
Generate Gamma presentations from analyzed slides.

Usage: python pipeline/generate_gamma_presentation.py <file_id>
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import asyncio
from tools.gamma_api import generate_presentation_from_file


async def main(file_id: int):
    """Generate Gamma presentation from slides."""
    result = await generate_presentation_from_file(file_id)

    print(f"\n✓ Presentation Generated!")
    print(f"View online: {result['gammaUrl']}")
    print(f"Download: {result['exportUrl']}")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline/generate_gamma_presentation.py <file_id>")
        sys.exit(1)

    file_id = int(sys.argv[1])
    asyncio.run(main(file_id))
