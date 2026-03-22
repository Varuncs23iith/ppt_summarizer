from openai import OpenAI
import os


def get_client()->OpenAI:
    """Create an instance of openai client.
    
    :return: OpenAI client.
    """
    return OpenAI(
        api_key = os.environ.get("OPENAI_API_KEY")
    )