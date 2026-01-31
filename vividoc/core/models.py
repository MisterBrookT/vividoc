"""Data models for vividoc pipeline."""

from pydantic import BaseModel, Field
from typing import List


class KnowledgeUnitSpec(BaseModel):
    """Specification for a single knowledge unit from Planner."""

    id: str = Field(description="Unique identifier for the knowledge unit")
    unit_content: str = Field(description="Brief summary of the knowledge unit")
    text_description: str = Field(
        description="Self-contained description for text generation"
    )
    interaction_description: str = Field(
        description="Self-contained description for interactive code generation"
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
