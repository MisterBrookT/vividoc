"""API route definitions."""

import json
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from vividoc.entrypoint.models import (
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
    ConfigUpdateRequest,
    doc_spec_to_api,
    api_to_doc_spec,
)
from vividoc.entrypoint.services import JobManager, SpecService, DocumentService

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


@router.get("/spec/{spec_id}/html", response_model=DocumentHTMLResponse)
async def get_spec_html(spec_id: str):
    """Get most recent HTML content for a spec."""
    try:
        html = document_service.get_html_for_spec(spec_id)
        if html:
            return DocumentHTMLResponse(html=html)
        else:
            raise HTTPException(status_code=404, detail="HTML not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history():
    """List all specification history."""
    try:
        specs = spec_service.list_specs()
        return {"history": specs}
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


@router.get("/jobs/{job_id}/html")
async def get_job_html(job_id: str):
    """Get current HTML content for a running or completed job.

    This endpoint allows real-time preview of the document being generated.
    Returns the current state of the HTML file, even if generation is still in progress.
    """
    try:
        job = job_manager.get_status(job_id)

        if job is None:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        # Get spec_id from job metadata (we need to store this when creating the job)
        # For now, try to get it from the result if job is completed
        if job.status == "completed" and job.result and "document_id" in job.result:
            # Job completed, get HTML from document service
            document_id = job.result["document_id"]
            html_content = document_service.get_html(document_id)
            return {"html": html_content, "status": "completed"}

        # Job is still running or failed
        # Try to read the HTML file directly from the spec output directory
        spec_id = document_service.get_spec_id_for_job(job_id)
        if spec_id:
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent.parent
            html_path = project_root / "outputs" / spec_id / "document.html"

            if html_path.exists():
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                return {"html": html_content, "status": job.status}

        # No HTML available yet
        return {"html": None, "status": job.status}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Configuration Endpoints


@router.get("/config")
async def get_config():
    """Get current configuration and available models."""
    from vividoc.core.config import AVAILABLE_LLM_MODELS
    from vividoc.entrypoint.models import ConfigResponse

    # Get current model from planner config
    current_model = spec_service.planner.config.llm_model

    return ConfigResponse(
        llm_model=current_model, available_models=sorted(list(AVAILABLE_LLM_MODELS))
    )


@router.put("/config")
async def update_config(request: ConfigUpdateRequest):
    """Update configuration (LLM model)."""
    from vividoc.core.config import RunnerConfig
    from vividoc.core import Planner, Evaluator
    from vividoc.entrypoint.models import ConfigResponse
    from vividoc.core.config import AVAILABLE_LLM_MODELS

    try:
        # Create new config with updated model
        new_config = RunnerConfig(llm_model=request.llm_model)

        # Update planner and evaluator
        spec_service.planner = Planner(new_config)
        document_service.config = new_config
        document_service.evaluator = Evaluator(new_config)

        return ConfigResponse(
            llm_model=request.llm_model,
            available_models=sorted(list(AVAILABLE_LLM_MODELS)),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chat Endpoint


class ChatRequest(BaseModel):
    """Request model for chat."""

    spec_id: str
    message: str
    stage: str = "doc"  # "spec" or "doc"


def _apply_edit_blocks(html: str, edit_blocks: list[dict]) -> str:
    """Apply structured edit blocks to HTML using BeautifulSoup.

    Each edit block has: action (replace|insert_after|append), target (CSS selector), content (HTML).
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    for block in edit_blocks:
        action = block.get("action", "").lower()
        target = block.get("target", "")
        content = block.get("content", "")

        if not target or not content:
            continue

        element = soup.select_one(target)
        if not element:
            continue

        content_soup = BeautifulSoup(content, "html.parser")

        if action == "replace":
            element.clear()
            for child in list(content_soup.children):
                element.append(child)
        elif action == "insert_after":
            for child in reversed(list(content_soup.children)):
                element.insert_after(child)
        elif action == "append":
            for child in list(content_soup.children):
                element.append(child)

    return str(soup)


def _parse_edit_blocks(text: str) -> list[dict]:
    """Parse ```edit ... ``` blocks from LLM response."""
    blocks = []
    # Relaxed pattern: allow optional whitespace/newlines around delimiters
    pattern = re.compile(r"```edit\s*(.*?)```", re.DOTALL)
    for match in pattern.finditer(text):
        block_text = match.group(1).strip()
        block: dict = {}
        # Parse ACTION, TARGET, CONTENT fields
        action_match = re.search(r"^ACTION:\s*(.+)$", block_text, re.MULTILINE)
        target_match = re.search(r"^TARGET:\s*(.+)$", block_text, re.MULTILINE)
        # CONTENT: everything after the CONTENT: line
        content_match = re.search(
            r"^CONTENT:\s*\n?(.*)", block_text, re.DOTALL | re.MULTILINE
        )
        if action_match:
            block["action"] = action_match.group(1).strip()
        if target_match:
            block["target"] = target_match.group(1).strip()
        if content_match:
            block["content"] = content_match.group(1).strip()
        if block.get("action") and block.get("target") and block.get("content"):
            blocks.append(block)
    return blocks


@router.post("/chat")
async def chat_stream(request: ChatRequest):
    """Stream LLM chat response via SSE.

    Supports two modes based on request.stage:
    - "doc": Edit HTML document (uses [EDIT_MODE] + ```edit blocks)
    - "spec": Edit specification (uses [SPEC_EDIT] + ```spec_json block)
    """
    import os

    dev_mode = os.environ.get("VIVIDOC_DEV", "0") == "1"

    try:
        from vividoc.utils.llm.client import LLMClient

        llm_client = LLMClient(spec_service.planner.config.llm_model)

        if request.stage == "spec":
            # Build spec editing prompt
            from prompts.chat_prompt import get_spec_edit_prompt

            try:
                internal_spec = spec_service.get_spec(request.spec_id)
            except KeyError:
                raise HTTPException(
                    status_code=404, detail=f"Spec not found: {request.spec_id}"
                )

            ku_lines = []
            for i, ku in enumerate(internal_spec.knowledge_units, 1):
                ku_lines.append(
                    f"  KU{i} (id={ku.id}):\n"
                    f"    Title: {ku.unit_content}\n"
                    f"    Description: {ku.text_description}\n"
                    f"    Interaction: {ku.interaction_description}"
                )
            ku_text = "\n".join(ku_lines)
            prompt = get_spec_edit_prompt(internal_spec.topic, ku_text, request.message)
            edit_marker = "[SPEC_EDIT]"
        else:
            # Build HTML editing prompt
            from prompts.chat_prompt import get_chat_edit_prompt

            html_content = document_service.get_html_for_spec(request.spec_id)
            if not html_content:
                html_content = "<p>No document generated yet.</p>"
            prompt = get_chat_edit_prompt(html_content, request.message)
            edit_marker = "[EDIT_MODE]"

        if dev_mode:
            print(f"\n{'=' * 60}")
            print(f"[CHAT DEV] stage={request.stage}, spec_id={request.spec_id}")
            print(f"[CHAT DEV] message={request.message}")
            print(f"[CHAT DEV] prompt length={len(prompt)} chars")
            print("[CHAT DEV] Streaming LLM response...")
            print(f"{'=' * 60}")

        def event_stream():
            full_response = ""
            is_edit_mode = False
            token_count = 0
            try:
                for token in llm_client.call_text_generation_stream(prompt):
                    full_response += token
                    token_count += 1
                    if dev_mode:
                        print(token, end="", flush=True)
                    if not is_edit_mode and edit_marker in full_response:
                        is_edit_mode = True
                        if dev_mode:
                            print(f"\n>>> [{edit_marker} detected] <<<")
                        data = json.dumps({"type": "edit_mode_start"})
                        yield f"data: {data}\n\n"
                    data = json.dumps({"type": "token", "content": token})
                    yield f"data: {data}\n\n"

                if dev_mode:
                    print(f"\n{'=' * 60}")
                    print(
                        f"[CHAT DEV] Done. tokens={token_count}, chars={len(full_response)}"
                    )
                    print(f"[CHAT DEV] edit_mode={is_edit_mode}")

                if is_edit_mode:
                    if request.stage == "spec":
                        # Parse spec JSON
                        spec_match = re.search(
                            r"```spec_json\s*(.*?)```", full_response, re.DOTALL
                        )
                        if spec_match:
                            import json as json_mod

                            spec_data = json_mod.loads(spec_match.group(1).strip())
                            if dev_mode:
                                print(
                                    f"[CHAT DEV] spec_json parsed: {len(spec_data.get('knowledge_units', []))} KUs"
                                )
                            # Convert to API format and update
                            from vividoc.core.models import (
                                DocumentSpec as InternalDocSpec,
                                KnowledgeUnitSpec,
                            )

                            new_kus = []
                            for ku_data in spec_data.get("knowledge_units", []):
                                new_kus.append(
                                    KnowledgeUnitSpec(
                                        id=ku_data.get("id", ""),
                                        unit_content=ku_data.get("title", ""),
                                        text_description=ku_data.get("description", ""),
                                        interaction_description=ku_data.get(
                                            "interaction_description", ""
                                        ),
                                    )
                                )
                            new_internal_spec = InternalDocSpec(
                                topic=spec_data.get("topic", ""),
                                knowledge_units=new_kus,
                            )
                            spec_service.update_spec(request.spec_id, new_internal_spec)
                            # Return updated spec in API format
                            api_spec = doc_spec_to_api(
                                new_internal_spec, request.spec_id
                            )
                            data = json.dumps(
                                {
                                    "type": "spec_updated",
                                    "spec": api_spec.model_dump(),
                                }
                            )
                            yield f"data: {data}\n\n"
                            if dev_mode:
                                print("[CHAT DEV] spec_updated event sent")
                    else:
                        # Parse HTML edit blocks
                        edit_blocks = _parse_edit_blocks(full_response)
                        if dev_mode:
                            print(f"[CHAT DEV] edit_blocks found={len(edit_blocks)}")
                            for i, b in enumerate(edit_blocks):
                                print(
                                    f"[CHAT DEV]   block[{i}]: action={b.get('action')}, target={b.get('target')}, content_len={len(b.get('content', ''))}"
                                )
                        if edit_blocks:
                            new_html = _apply_edit_blocks(html_content, edit_blocks)
                            project_root = Path(__file__).parent.parent.parent.parent
                            html_path = (
                                project_root
                                / "outputs"
                                / request.spec_id
                                / "document.html"
                            )
                            html_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(html_path, "w", encoding="utf-8") as f:
                                f.write(new_html)
                            if dev_mode:
                                print(f"[CHAT DEV] HTML saved ({len(new_html)} chars)")
                            data = json.dumps(
                                {"type": "html_updated", "html": new_html}
                            )
                            yield f"data: {data}\n\n"

                if dev_mode:
                    print(f"{'=' * 60}\n")

                data = json.dumps({"type": "done"})
                yield f"data: {data}\n\n"
            except Exception as e:
                if dev_mode:
                    import traceback

                    print(f"\n[CHAT DEV] ERROR: {e}")
                    traceback.print_exc()
                data = json.dumps({"type": "error", "content": str(e)})
                yield f"data: {data}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
