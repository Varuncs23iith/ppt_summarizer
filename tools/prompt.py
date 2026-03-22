import yaml
from jinja2 import Environment, StrictUndefined, select_autoescape
from pathlib import Path


def get_prompt_from_file(
    file_path: Path,
    prompt_type: str,
    **kwargs
) -> str:
    """Return tool prompt hydrated with provided kwargs.

    :param file_path: llm instruction file path.
    :param prompt_type: system or user prompt.
    :param kwargs: other kwargs.
    :return: llm instructions to follow.
    """
    with open(file_path, "r") as f:
        prompt_data = yaml.safe_load(file_path.read_text())
    
    prompt_data = prompt_data[prompt_type]
    environment = Environment(undefined=StrictUndefined, 
                              autoescape=False)

    jinja_ = environment.from_string(prompt_data)
    return jinja_.render(**kwargs)