"""Data models for vividoc pipeline."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class InteractionSpec(BaseModel):
    """Structured interaction specification using (S, R, T, C) decomposition."""

    state: Dict[str, Any] = Field(
        description="State variables: keys are variable names, values describe control type, range, derivation"
    )
    render: List[str] = Field(
        description="List of visual elements describing how state maps to visuals"
    )
    transition: List[str] = Field(
        description="List of interaction rules describing how user actions change state"
    )
    constraint: Optional[str] = Field(
        default=None,
        description="Pedagogical invariant — what the learner should observe",
    )


class KnowledgeUnitSpec(BaseModel):
    """Specification for a single knowledge unit from Planner."""

    id: str = Field(description="Unique identifier for the knowledge unit")
    unit_content: str = Field(description="Brief summary of the knowledge unit")
    text_description: str = Field(
        description="Self-contained description for text generation"
    )
    interaction_spec: InteractionSpec = Field(
        description="Structured interaction specification (S, R, T, C)"
    )


class DocumentSpec(BaseModel):
    """Complete document specification from Planner."""

    topic: str = Field(description="The topic of the document")
    knowledge_units: List[KnowledgeUnitSpec] = Field(
        description="List of knowledge units"
    )


class KnowledgeUnitState(BaseModel):
    """Generation state for a single knowledge unit."""

    id: str = Field(description="Unique identifier matching the spec")
    unit_content: str = Field(description="Brief summary from spec")

    # Status flags only (no HTML content stored)
    stage1_completed: bool = Field(
        default=False, description="Whether Stage 1 is completed"
    )
    stage2_completed: bool = Field(
        default=False, description="Whether Stage 2 is completed"
    )
    validated: bool = Field(
        default=False, description="Whether the HTML has been validated"
    )


class GeneratedDocument(BaseModel):
    """Complete generated document."""

    topic: str = Field(description="The topic of the document")
    html_file_path: str = Field(description="Path to the generated HTML file")
    knowledge_units: List[KnowledgeUnitState] = Field(
        description="List of knowledge unit states"
    )


class EvaluationFeedback(BaseModel):
    """Evaluation feedback from Evaluator."""

    overall_coherence: str = Field(
        description="Assessment of text fluency and logical flow"
    )
    component_issues: List[str] = Field(
        description="List of issues found in interactive components"
    )
    requires_revision: bool = Field(description="Whether the document needs revision")


class StyleConfig(BaseModel):
    """User style preferences for document generation."""

    text_density: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Text density: 1=minimal, 3=balanced, 5=detailed",
    )
    tone: str = Field(
        default="conversational",
        description="Writing tone: academic, conversational, playful",
    )
    interaction_style: str = Field(
        default="rich",
        description="Interaction style: minimal, balanced, rich",
    )
    color_scheme: str = Field(
        default="auto",
        description="Color scheme: auto, indigo, emerald, rose, amber, slate",
    )
