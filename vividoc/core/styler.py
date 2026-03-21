"""Styler module — converts user style preferences into prompt instructions."""

from vividoc.core.models import StyleConfig

# Fixed style options for frontend rendering
STYLE_OPTIONS = {
    "text_density": {
        "label": "Text Density",
        "type": "slider",
        "min": 1,
        "max": 5,
        "default": 3,
        "labels": {
            1: "Minimal",
            2: "Brief",
            3: "Balanced",
            4: "Detailed",
            5: "Comprehensive",
        },
        "descs": {
            1: "Use very concise text. Only essential explanations, no elaboration.",
            2: "Use brief text. Short paragraphs with key points only.",
            3: "Use balanced text. Clear explanations with moderate detail.",
            4: "Use detailed text. Thorough explanations with examples.",
            5: "Use very detailed text. Comprehensive coverage with rich examples and analogies.",
        },
    },
    "tone": {
        "label": "Writing Tone",
        "type": "radio",
        "choices": [
            {
                "value": "academic",
                "label": "Academic",
                "desc": "Formal, precise, structured",
            },
            {
                "value": "conversational",
                "label": "Conversational",
                "desc": "Friendly, approachable, clear",
            },
            {
                "value": "playful",
                "label": "Playful",
                "desc": "Fun, engaging, adventurous",
            },
        ],
        "default": "conversational",
    },
    "interaction_style": {
        "label": "Interaction Style",
        "type": "radio",
        "choices": [
            {
                "value": "minimal",
                "label": "Minimal",
                "desc": "Simple controls, clarity first",
            },
            {
                "value": "balanced",
                "label": "Balanced",
                "desc": "Smooth transitions, intuitive",
            },
            {"value": "rich", "label": "Rich", "desc": "Animated, visually engaging"},
        ],
        "default": "rich",
    },
    "color_scheme": {
        "label": "Color Scheme",
        "type": "color",
        "choices": [
            {"value": "auto", "label": "Auto"},
            {"value": "indigo", "label": "Indigo", "hex": "#4f46e5"},
            {"value": "emerald", "label": "Emerald", "hex": "#059669"},
            {"value": "rose", "label": "Rose", "hex": "#e11d48"},
            {"value": "amber", "label": "Amber", "hex": "#d97706"},
            {"value": "slate", "label": "Slate", "hex": "#475569"},
        ],
        "default": "auto",
    },
}


_DENSITY_MAP = {
    1: "Use very concise text. Only essential explanations, no elaboration.",
    2: "Use brief text. Short paragraphs with key points only.",
    3: "Use balanced text. Clear explanations with moderate detail.",
    4: "Use detailed text. Thorough explanations with examples.",
    5: "Use very detailed text. Comprehensive coverage with rich examples and analogies.",
}

_TONE_MAP = {
    "academic": "Use a formal academic tone. Precise terminology, structured arguments, citations-style references where appropriate.",
    "conversational": "Use a friendly conversational tone. Explain concepts as if talking to a curious friend. Use 'we' and 'you'.",
    "playful": "Use a fun, playful tone. Include analogies, humor, and engaging language. Make learning feel like an adventure.",
}

_INTERACTION_MAP = {
    "minimal": "Use simple, minimal interactive controls (basic sliders, buttons). Prioritize clarity over visual flair.",
    "balanced": "Use a balanced mix of controls and visualizations. Include smooth transitions but keep interactions intuitive.",
    "rich": "Use rich, animated interactive elements. Include smooth CSS/JS animations, hover effects, and visually engaging transitions.",
}


class Styler:
    """Converts style preferences into prompt instructions."""

    @staticmethod
    def get_options() -> dict:
        """Return the fixed style options for frontend rendering."""
        return STYLE_OPTIONS

    @staticmethod
    def to_prompt_instructions(config: StyleConfig | None = None) -> str:
        """Convert a StyleConfig into a prompt instruction block."""
        if config is None:
            config = StyleConfig()

        lines = [
            "=== STYLE PREFERENCES ===",
            _DENSITY_MAP.get(config.text_density, _DENSITY_MAP[3]),
            _TONE_MAP.get(config.tone, _TONE_MAP["conversational"]),
            _INTERACTION_MAP.get(config.interaction_style, _INTERACTION_MAP["rich"]),
        ]
        if config.color_scheme and config.color_scheme != "auto":
            lines.append(
                f"Color scheme: use '{config.color_scheme}' as the primary accent color for interactive elements."
            )
        return "\n".join(lines)
