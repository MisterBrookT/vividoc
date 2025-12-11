from PIL.Image import Image as PILImage
from typing import Any
from .caller_registry import register_caller
from google import genai
from google.genai import types
from openai import OpenAI
import os

class LLMCaller():
    def generate_text(self, model: str, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError

    def understand_image(
        self, model: str, prompt: str, image_path: str, **kwargs: Any
    ) -> str:
        raise NotImplementedError

    def generate_image(self, model: str, prompt: str, **kwargs: Any) -> PILImage:
        raise NotImplementedError


@register_caller("google")
class GoogleCaller(LLMCaller):
    def __init__(self) -> None:
        self._client = genai.Client()

    def generate_text(self, model: str, prompt: str, **kwargs: Any) -> str:
        response = self._client.models.generate_content(model=model, contents=prompt)
        return response.text

    def understand_image(
        self, model: str, prompt: str, image_path: str, **kwargs: Any
    ) -> str:
        if prompt is None:
            raise ValueError("Prompt cannot be None")
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        response = self._client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt,
            ],
        )
        return response.text