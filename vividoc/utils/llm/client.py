from typing import Any, Type

from .caller_registry import CALLER_REGISTRY
from PIL.Image import Image as PILImage
from ..io import extract_from_markdown
from .llm_caller import LLMCaller
from pydantic import BaseModel


class LLMClient:
    def __init__(self, llm_model: str):
        """
        Initialize LLM client with model string.

        Args:
            llm_model: Model string in format "provider/model-name"
                      e.g., "openrouter/google/gemini-2.5-pro" or "google/gemini-2.5-pro"
        """
        provider, model = self._parse_llm_model(llm_model)
        self._caller = self._get_caller(provider)
        self.model = model

    def _parse_llm_model(self, llm_model: str) -> tuple[str, str]:
        """
        Parse llm_model string into provider and model name.

        Args:
            llm_model: Model string in format "provider/model-name"

        Returns:
            Tuple of (provider, model_name)

        Raises:
            ValueError: If format is invalid
        """
        if "/" not in llm_model:
            raise ValueError(
                f"Invalid llm_model format: '{llm_model}'. "
                f"Expected format: 'provider/model-name' (e.g., 'openrouter/google/gemini-2.5-pro')"
            )

        parts = llm_model.split("/", 1)
        provider = parts[0]
        model_name = parts[1]

        return provider, model_name

    def _get_caller(self, provider: str) -> LLMCaller:
        provider = provider.lower()
        if provider not in CALLER_REGISTRY:
            raise ValueError(
                f"Unsupported provider: {provider}. Supported providers: {list(CALLER_REGISTRY.keys())}"
            )
        return CALLER_REGISTRY[provider]()

    def call_text_generation(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using the configured model."""
        text_response = self._caller.generate_text(self.model, prompt, **kwargs)
        style_normalized_text_response = extract_from_markdown(text_response)
        return style_normalized_text_response

    def call_image_understanding(
        self, prompt: str, image_path: str, **kwargs: Any
    ) -> str:
        """Understand image using the configured model."""
        text_response = self._caller.understand_image(
            self.model, prompt, image_path, **kwargs
        )
        style_normalized_text_response = extract_from_markdown(text_response)
        return style_normalized_text_response

    def call_image_generation(self, prompt: str, **kwargs: Any) -> PILImage:
        """Generate image using the configured model."""
        pil_image = self._caller.generate_image(self.model, prompt, **kwargs)
        return pil_image

    def call_structured_output(
        self, prompt: str, schema: Type[BaseModel], **kwargs: Any
    ) -> BaseModel:
        """Call LLM with structured output using Pydantic schema."""
        response = self._caller.generate_structured(
            self.model, prompt, schema, **kwargs
        )
        return schema.model_validate_json(response)
