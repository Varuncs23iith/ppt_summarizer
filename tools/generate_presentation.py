"""
Simple interface for generating Gamma presentations.
"""

import asyncio
from tools.gamma_api import generate_presentation_from_file


def generate_gamma_presentation(file_id: int) -> dict:
    """Generate Gamma presentation (synchronous)."""
    return asyncio.run(generate_presentation_from_file(file_id))


async def generate_gamma_presentation_async(file_id: int) -> dict:
    """Generate Gamma presentation (async)."""
    return await generate_presentation_from_file(file_id)
