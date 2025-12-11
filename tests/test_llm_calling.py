import pytest
from vividoc.utils.llm.client import LLMClient
from vividoc.utils.logger import logger


@pytest.fixture
def google_client():
    """Fixture to create LLMClient with google provider."""
    return LLMClient("google")

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


def test_google_gemini_2_5_pro():
    """Test Google gemini-2.5-pro model."""
    setup_test_suite("google", "gemini-2.5-pro")

