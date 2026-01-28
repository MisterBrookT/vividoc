import json
import re
from pathlib import Path
from typing import Type
from pydantic import BaseModel
from vividoc.utils.logger import logger


def extract_from_markdown(text: str) -> dict | str:
    """
    Extract content from LLM response with fenced code block.
    If no code block found, return original text.
    """
    # Match any fenced code block: ```lang or just ```
    pattern = r"```(?:\w+)?\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        content = match.group(1).strip()
        # Try JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    # No code block, return original text
    return text


def save_json(data: BaseModel, file_path: str) -> None:
    """Save Pydantic model to JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data.model_dump_json(indent=2))
    
    logger.info(f"Saved to {file_path}")


def load_json(file_path: str, model: Type[BaseModel]) -> BaseModel:
    """Load and validate JSON against Pydantic model."""
    path = Path(file_path)
    
    with open(path, 'r', encoding='utf-8') as f:
        json_str = f.read()
    
    instance = model.model_validate_json(json_str)
    logger.info(f"Loaded from {file_path}")
    return instance