"""Tests for RunnerConfig and model validation."""

import pytest
from vividoc.core.config import RunnerConfig, AVAILABLE_LLM_MODELS


class TestValidateLLMModel:
    """Tests for RunnerConfig.validate_llm_model static method."""

    def test_valid_google_model(self):
        """Test that valid Google models are accepted."""
        RunnerConfig.validate_llm_model("google/gemini-2.5-pro")
        # Should not raise

    def test_valid_openrouter_model(self):
        """Test that valid OpenRouter models are accepted."""
        RunnerConfig.validate_llm_model("openrouter/google/gemini-2.5-pro")
        RunnerConfig.validate_llm_model("openrouter/moonshotai/kimi-k2.5")
        # Should not raise

    def test_invalid_model_raises_error(self):
        """Test that invalid models raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RunnerConfig.validate_llm_model("invalid/model")

        error_msg = str(exc_info.value)
        assert "Invalid llm_model: 'invalid/model'" in error_msg
        assert "Available models:" in error_msg

    def test_invalid_format_raises_error(self):
        """Test that models without provider raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RunnerConfig.validate_llm_model("gemini-2.5-pro")

        error_msg = str(exc_info.value)
        assert "Invalid llm_model" in error_msg

    def test_all_available_models_are_valid(self):
        """Test that all models in AVAILABLE_LLM_MODELS are valid."""
        for model in AVAILABLE_LLM_MODELS:
            # Should not raise
            RunnerConfig.validate_llm_model(model)


class TestRunnerConfig:
    """Tests for RunnerConfig class."""

    def test_default_config_is_valid(self):
        """Test that default configuration is valid."""
        config = RunnerConfig()
        assert config.llm_model in AVAILABLE_LLM_MODELS

    def test_valid_model_accepted(self):
        """Test that valid models are accepted in config."""
        config = RunnerConfig(llm_model="google/gemini-2.5-pro")
        assert config.llm_model == "google/gemini-2.5-pro"

    def test_invalid_model_rejected(self):
        """Test that invalid models are rejected in config."""
        with pytest.raises(ValueError) as exc_info:
            RunnerConfig(llm_model="invalid/model")

        error_msg = str(exc_info.value)
        assert "Invalid llm_model" in error_msg

    def test_config_with_all_parameters(self):
        """Test config with all parameters set."""
        config = RunnerConfig(
            llm_model="openrouter/moonshotai/kimi-k2.5",
            max_fix_attempts=5,
            output_dir="custom_output",
            resume=True,
            plan_only=True,
            execute_only=False,
            evaluate_only=False,
        )

        assert config.llm_model == "openrouter/moonshotai/kimi-k2.5"
        assert config.max_fix_attempts == 5
        assert config.output_dir == "custom_output"
        assert config.resume is True
        assert config.plan_only is True

    def test_available_models_set_not_empty(self):
        """Test that AVAILABLE_LLM_MODELS is not empty."""
        assert len(AVAILABLE_LLM_MODELS) > 0

    def test_available_models_have_correct_format(self):
        """Test that all available models have correct format."""
        for model in AVAILABLE_LLM_MODELS:
            assert "/" in model, f"Model {model} should contain '/'"
            parts = model.split("/")
            assert len(parts) >= 2, f"Model {model} should have at least provider/model"
