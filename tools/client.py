from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_client()->OpenAI:
    """Create an instance of openai client.

    :return: OpenAI client.
    """
    api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please set it in .env file or environment variables."
        )
    return OpenAI(api_key=api_key)