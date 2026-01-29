"""API route definitions."""

from fastapi import APIRouter, HTTPException, Response
from backend.models import (
    SpecGenerateRequest,
    SpecGenerateResponse,
    SpecUpdateRequest,
    DocumentGenerateRequest,
    DocumentGenerateResponse,
    JobStatusResponse,
    DocumentMetadataResponse,
    DocumentHTMLResponse,
    ProgressInfo as APIProgressInfo,
    KUProgress as APIKUProgress,
    doc_spec_to_api,
    api_to_doc_spec,
)
from backend.services import JobManager, SpecService, DocumentService

# Create router
router = APIRouter(prefix="/api")

# These will be initialized in main.py
job_manager: JobManager = None
spec_service: SpecService = None
document_service: DocumentService = None


def init_services(jm: JobManager, ss: SpecService, ds: DocumentService):
    """Initialize service instances."""
    global job_manager, spec_service, document_service
    job_manager = jm
    spec_service = ss
    document_service = ds


# Spec Management Endpoints


@router.post("/spec/generate", response_model=SpecGenerateResponse)
async def generate_spec(request: SpecGenerateRequest):
    """Generate a document specification from a topic.

    Args:
        request: SpecGenerateRequest containing the topic

    Returns:
        SpecGenerateResponse with spec_id and generated spec

    Raises:
        HTTPException 400: If topic is empty or invalid
        HTTPException 500: If spec generation fails
    """
    try:
        # Validate topic is not empty
        if not request.topic or not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty")

        spec_id, spec = spec_service.generate_spec(request.topic)
        # Convert internal DocumentSpec to API format
        api_spec = doc_spec_to_api(spec, spec_id)
        return SpecGenerateResponse(spec_id=spec_id, spec=api_spec)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spec/{spec_id}")
async def get_spec(spec_id: str):
    """Retrieve a specification by ID.

    Args:
        spec_id: Unique identifier for the spec

    Returns:
        Dict containing the spec

    Raises:
        HTTPException 400: If spec_id is empty
        HTTPException 404: If spec not found
        HTTPException 500: If retrieval fails
    """
    try:
        # Validate spec_id is not empty
        if not spec_id or not spec_id.strip():
            raise HTTPException(status_code=400, detail="Spec ID cannot be empty")

        spec = spec_service.get_spec(spec_id)
        # Convert internal DocumentSpec to API format
        api_spec = doc_spec_to_api(spec, spec_id)
        return {"spec": api_spec}
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Spec not found: {spec_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/spec/{spec_id}")
async def update_spec(spec_id: str, request: SpecUpdateRequest):
    """Update an existing specification.

    Args:
        spec_id: Unique identifier for the spec
        request: SpecUpdateRequest containing the updated spec

    Returns:
        Dict containing the updated spec

    Raises:
        HTTPException 400: If spec_id is empty or spec is invalid
        HTTPException 404: If spec not found
        HTTPException 500: If update fails
    """
    try:
        # Validate spec_id is not empty
        if not spec_id or not spec_id.strip():
            raise HTTPException(status_code=400, detail="Spec ID cannot be empty")

        # Validate spec has required fields
        if not request.spec.topic or not request.spec.topic.strip():
            raise HTTPException(status_code=400, detail="Spec topic cannot be empty")

        # Convert API format to internal DocumentSpec
        internal_spec = api_to_doc_spec(request.spec)
        updated_spec = spec_service.update_spec(spec_id, internal_spec)
        # Convert back to API format
        api_spec = doc_spec_to_api(updated_spec, spec_id)
        return {"spec": api_spec}
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Spec not found: {spec_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Document Generation Endpoints


@router.post("/document/generate", response_model=DocumentGenerateResponse)
async def generate_document(request: DocumentGenerateRequest):
    """Start document generation from a specification."""
    try:
        # Get spec
        spec = spec_service.get_spec(request.spec_id)

        # Start generation job
        job_id = document_service.generate_document(request.spec_id, spec)

        return DocumentGenerateResponse(job_id=job_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Spec not found: {request.spec_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}", response_model=DocumentMetadataResponse)
async def get_document(document_id: str):
    """Retrieve document metadata."""
    try:
        doc_metadata = document_service.get_document(document_id)
        return DocumentMetadataResponse(**doc_metadata)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Document not found: {document_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}/html", response_model=DocumentHTMLResponse)
async def get_document_html(document_id: str):
    """Retrieve document HTML content."""
    try:
        html_content = document_service.get_html(document_id)
        return DocumentHTMLResponse(html=html_content)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Document not found: {document_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}/download")
async def download_document(document_id: str):
    """Download document as HTML file."""
    try:
        html_content = document_service.get_html(document_id)

        # Return HTML file with download headers
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename=document_{document_id}.html"
            },
        )
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Document not found: {document_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Job Management Endpoints


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status and progress information."""
    try:
        job = job_manager.get_status(job_id)

        if job is None:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        # Convert service-layer progress to API model
        api_progress = APIProgressInfo(
            phase=job.progress.phase,
            overall_percent=job.progress.overall_percent,
            current_ku=job.progress.current_ku,
            ku_stage=job.progress.ku_stage,
            ku_progress=[
                APIKUProgress(ku_id=ku.ku_id, title=ku.title, status=ku.status)
                for ku in job.progress.ku_progress
            ],
        )

        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=api_progress,
            result=job.result,
            error=job.error,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
