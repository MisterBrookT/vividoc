import pytest
from pydantic import BaseModel, Field
from vividoc.utils.llm.client import LLMClient
from vividoc.utils.logger import logger


class MathAnswer(BaseModel):
    """Schema for structured math answer."""

    answer: str = Field(description="The answer to the math question")
    explanation: str = Field(description="Brief explanation of the answer")


@pytest.fixture
def google_client():
    """Fixture to create LLMClient with google provider."""
    return LLMClient("google")


@pytest.fixture
def openrouter_client():
    """Fixture to create LLMClient with google provider."""
    return LLMClient("openrouter")


def setup_test_data():
    """Setup test data and image for CLI tests"""
    topic = "what is pi? tell me in one sentence"
    return topic


def setup_test_suite(provider: str, model: str):
    """Test suite for different model types."""
    client = LLMClient(provider)
    # Test text generation
    prompt = setup_test_data()
    result = client.call_text_generation(model, prompt)
    logger.info(f"result: {result}")
    assert "pi" in result or "π" in result or "Pi" in result


# def test_google_gemini_3_flash():
# """Test Google gemini-3-flash model."""
# setup_test_suite("google", "gemini-3-flash-preview")


def test_openrouter_kimi_k_2_5():
    """Test OpenRouter kimi-k-2.5 model."""
    setup_test_suite("openrouter", "moonshotai/kimi-k2.5")


def setup_structured_test_suite(provider: str, model: str):
    """Test suite for structured output."""
    client = LLMClient(provider)
    prompt = "What is pi?"
    result = client.call_structured_output(model, prompt, MathAnswer)

    logger.info(f"Structured result: {result}")
    assert isinstance(result, MathAnswer)
    assert result.answer
    assert result.explanation
    assert (
        "pi" in result.answer.lower() or "π" in result.answer or "3.14" in result.answer
    )


def test_openrouter_kimi_structured():
    """Test OpenRouter kimi with structured output."""
    setup_structured_test_suite("openrouter", "moonshotai/kimi-k2.5")
