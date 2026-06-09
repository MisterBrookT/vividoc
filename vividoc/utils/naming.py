"""Shared naming utilities for topic-based directory names."""

import hashlib
import re
import uuid


def topic_to_dirname(topic: str) -> str:
    """Sanitize topic string into a filesystem-safe directory name.

    Example: "Fourier Transform" -> "fourier_transform"
    """
    name = topic.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "_", name)
    return name[:120]


def model_to_method_suffix(model: str) -> str:
    """Extract a short model name from a full model string for use as method suffix.

    Examples:
        "openrouter/google/gemini-3-flash-preview" -> "gemini-3-flash"
        "google/gemini-3-flash-preview"            -> "gemini-3-flash"
        "openai/gpt-4o"                            -> "gpt-4o"
        "openrouter/openai/gpt-5.4"                -> "gpt-5.4"
    """
    # Strip provider prefixes (openrouter/, google/, openai/, etc.)
    name = model.split("/")[-1]
    # Remove common suffixes: -preview, -latest
    name = re.sub(r"-(preview|latest)$", "", name)
    return name


def topic_to_uuid(topic: str, *, deterministic: bool = True, salt: str = "") -> str:
    """Generate UUID from topic.

    Args:
        topic: The topic string.
        deterministic: If True, same topic always produces same UUID.
                       If False, includes timestamp for uniqueness.
        salt: Extra string mixed in (e.g. timestamp) when deterministic=False.

    Returns:
        UUID string (full 32-char hex).
    """
    source = f"{topic}_{salt}" if salt else topic
    hash_obj = hashlib.md5(source.encode("utf-8"))
    return str(uuid.UUID(hash_obj.hexdigest()))


def make_output_dirname(topic: str, topic_uuid: str) -> str:
    """Build a human-readable output directory name.

    Format: {topic_name}_{uuid_short}
    Example: "fourier_transform_a1b2c3d4"
    """
    short_uuid = topic_uuid.replace("-", "")[:8]
    return f"{topic_to_dirname(topic)}_{short_uuid}"
