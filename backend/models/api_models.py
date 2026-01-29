"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from vividoc.models import DocumentSpec, KnowledgeUnitSpec


class KnowledgeUnit(BaseModel):
    """API model for a knowledge unit (frontend-facing)."""

    id: str = Field(description="Unique identifier for the knowledge unit")
    title: str = Field(description="Title of the knowledge unit")
    description: str = Field(description="Description of the knowledge unit")
    learning_objectives: List[str] = Field(
        default_factory=list, description="List of learning objectives"
    )
    prerequisites: List[str] = Field(
        default_factory=list, description="List of prerequisites"
    )


class DocumentSpecAPI(BaseModel):
    """API model for document specification (frontend-facing)."""

    id: str = Field(default="", description="Spec identifier (set by frontend)")
    topic: str = Field(description="The topic of the document")
    knowledge_units: List[KnowledgeUnit] = Field(description="List of knowledge units")
    metadata: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Metadata (created_at, updated_at)"
    )


def ku_spec_to_api(ku_spec: KnowledgeUnitSpec) -> KnowledgeUnit:
    """Convert internal KnowledgeUnitSpec to API KnowledgeUnit."""
    return KnowledgeUnit(
        id=ku_spec.id,
        title=ku_spec.unit_content,
        description=ku_spec.text_description,
        learning_objectives=[],  # Not available in KnowledgeUnitSpec
        prerequisites=[],  # Not available in KnowledgeUnitSpec
    )


def api_to_ku_spec(ku_api: KnowledgeUnit) -> KnowledgeUnitSpec:
    """Convert API KnowledgeUnit to internal KnowledgeUnitSpec."""
    return KnowledgeUnitSpec(
        id=ku_api.id,
        unit_content=ku_api.title,
        text_description=ku_api.description,
        interaction_description=ku_api.description,  # Use same description for both
    )


def doc_spec_to_api(doc_spec: DocumentSpec, spec_id: str = "") -> DocumentSpecAPI:
    """Convert internal DocumentSpec to API DocumentSpecAPI."""
    return DocumentSpecAPI(
        id=spec_id,
        topic=doc_spec.topic,
        knowledge_units=[ku_spec_to_api(ku) for ku in doc_spec.knowledge_units],
        metadata={
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )


def api_to_doc_spec(doc_api: DocumentSpecAPI) -> DocumentSpec:
    """Convert API DocumentSpecAPI to internal DocumentSpec."""
    return DocumentSpec(
        topic=doc_api.topic,
        knowledge_units=[api_to_ku_spec(ku) for ku in doc_api.knowledge_units],
    )


class SpecGenerateRequest(BaseModel):
    """Request model for spec generation."""

    topic: str = Field(description="The topic for document generation")


class SpecGenerateResponse(BaseModel):
    """Response model for spec generation."""

    spec_id: str = Field(description="Unique identifier for the generated spec")
    spec: DocumentSpecAPI = Field(description="The generated document specification")


class SpecUpdateRequest(BaseModel):
    """Request model for spec updates."""

    spec: DocumentSpecAPI = Field(description="The updated document specification")


class DocumentGenerateRequest(BaseModel):
    """Request model for document generation."""

    spec_id: str = Field(description="The spec ID to generate document from")


class DocumentGenerateResponse(BaseModel):
    """Response model for document generation."""

    job_id: str = Field(description="Unique identifier for the generation job")


class KUProgress(BaseModel):
    """Progress information for a single knowledge unit."""

    ku_id: str = Field(description="Knowledge unit identifier")
    title: str = Field(description="Knowledge unit title/content")
    status: str = Field(
        description="Current status: pending, stage1, stage2, or completed"
    )


class ProgressInfo(BaseModel):
    """Progress information for a job."""

    phase: str = Field(description="Current phase: planning, executing, or evaluating")
    overall_percent: float = Field(description="Overall progress percentage (0-100)")
    current_ku: Optional[str] = Field(
        default=None, description="Currently processing knowledge unit ID"
    )
    ku_stage: Optional[str] = Field(
        default=None, description="Current KU stage: stage1 or stage2"
    )
    ku_progress: List[KUProgress] = Field(
        default_factory=list, description="Progress for each knowledge unit"
    )


class JobStatusResponse(BaseModel):
    """Response model for job status."""

    job_id: str = Field(description="Job identifier")
    status: str = Field(description="Job status: running, completed, or failed")
    progress: ProgressInfo = Field(description="Progress information")
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Result data when job completes"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if job failed"
    )


class DocumentMetadataResponse(BaseModel):
    """Response model for document metadata."""

    document_id: str = Field(description="Document identifier")
    created_at: str = Field(description="Creation timestamp")
    spec_id: str = Field(description="Associated spec identifier")


class DocumentHTMLResponse(BaseModel):
    """Response model for document HTML content."""

    html: str = Field(description="HTML content of the document")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(description="Error message")
    detail: Optional[str] = Field(
        default=None, description="Detailed error information"
    )
