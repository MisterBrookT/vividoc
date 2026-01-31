"""Unit tests for API routes."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from vividoc.core.models import DocumentSpec, KnowledgeUnitSpec

from vividoc.entrypoint.web_server import create_app
from vividoc.entrypoint.api.routes import init_services
from vividoc.entrypoint.services import JobManager, SpecService, DocumentService
from vividoc.entrypoint.models import doc_spec_to_api


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    job_manager = Mock(spec=JobManager)
    spec_service = Mock(spec=SpecService)
    document_service = Mock(spec=DocumentService)

    # Initialize routes with mock services
    init_services(job_manager, spec_service, document_service)

    return {
        "job_manager": job_manager,
        "spec_service": spec_service,
        "document_service": document_service,
    }


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_spec():
    """Create a sample DocumentSpec for testing."""
    return DocumentSpec(
        topic="Python Programming",
        knowledge_units=[
            KnowledgeUnitSpec(
                id="ku-1",
                unit_content="Introduction to Python",
                text_description="Learn Python basics and syntax",
                interaction_description="Interactive Python code examples",
            ),
            KnowledgeUnitSpec(
                id="ku-2",
                unit_content="Data Structures",
                text_description="Learn about lists, dicts, sets",
                interaction_description="Interactive data structure examples",
            ),
        ],
    )


class TestSpecGenerationEndpoint:
    """Tests for POST /api/spec/generate endpoint."""

    def test_generate_spec_success(self, client, mock_services, sample_spec):
        """Test successful spec generation."""
        # Setup mock
        mock_services["spec_service"].generate_spec.return_value = (
            "test-spec-id",
            sample_spec,
        )

        # Make request
        response = client.post(
            "/api/spec/generate", json={"topic": "Python Programming"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "spec_id" in data
        assert data["spec_id"] == "test-spec-id"
        assert "spec" in data
        assert data["spec"]["topic"] == "Python Programming"

        # Verify service was called
        mock_services["spec_service"].generate_spec.assert_called_once_with(
            "Python Programming"
        )

    def test_generate_spec_empty_topic(self, client, mock_services):
        """Test spec generation with empty topic."""
        response = client.post("/api/spec/generate", json={"topic": ""})

        # Should return 400 for empty topic
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "empty" in response.json()["detail"].lower()

    def test_generate_spec_whitespace_topic(self, client, mock_services):
        """Test spec generation with whitespace-only topic."""
        response = client.post("/api/spec/generate", json={"topic": "   "})

        # Should return 400 for whitespace-only topic
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "empty" in response.json()["detail"].lower()

    def test_generate_spec_missing_topic(self, client, mock_services):
        """Test spec generation with missing topic field."""
        response = client.post("/api/spec/generate", json={})

        # FastAPI should return 422 for missing required field
        assert response.status_code == 422

    def test_generate_spec_service_error(self, client, mock_services):
        """Test spec generation when service raises an error."""
        # Setup mock to raise exception
        mock_services["spec_service"].generate_spec.side_effect = Exception(
            "Planner failed"
        )

        # Make request
        response = client.post("/api/spec/generate", json={"topic": "Test Topic"})

        # Should return 500 error
        assert response.status_code == 500
        assert "detail" in response.json()


class TestGetSpecEndpoint:
    """Tests for GET /api/spec/{spec_id} endpoint."""

    def test_get_spec_success(self, client, mock_services, sample_spec):
        """Test successful spec retrieval."""
        # Setup mock
        mock_services["spec_service"].get_spec.return_value = sample_spec

        # Make request
        response = client.get("/api/spec/test-spec-id")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "spec" in data
        assert data["spec"]["topic"] == "Python Programming"

        # Verify service was called
        mock_services["spec_service"].get_spec.assert_called_once_with("test-spec-id")

    def test_get_spec_not_found(self, client, mock_services):
        """Test retrieving non-existent spec."""
        # Setup mock to raise KeyError
        mock_services["spec_service"].get_spec.side_effect = KeyError(
            "Spec not found: invalid-id"
        )

        # Make request
        response = client.get("/api/spec/invalid-id")

        # Should return 404
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "not found" in response.json()["detail"].lower()

    def test_get_spec_empty_id(self, client, mock_services):
        """Test retrieving spec with empty ID."""
        # Make request with empty ID (URL encoded space)
        response = client.get("/api/spec/%20")

        # Should return 400 for empty ID
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_get_spec_service_error(self, client, mock_services):
        """Test get spec when service raises unexpected error."""
        # Setup mock to raise exception
        mock_services["spec_service"].get_spec.side_effect = Exception("Database error")

        # Make request
        response = client.get("/api/spec/test-id")

        # Should return 500
        assert response.status_code == 500


class TestUpdateSpecEndpoint:
    """Tests for PUT /api/spec/{spec_id} endpoint."""

    def test_update_spec_success(self, client, mock_services, sample_spec):
        """Test successful spec update."""
        # Modify the spec
        updated_spec = DocumentSpec(
            topic="Advanced Python", knowledge_units=sample_spec.knowledge_units
        )

        # Setup mock
        mock_services["spec_service"].update_spec.return_value = updated_spec

        # Convert to API format for request
        api_spec = doc_spec_to_api(updated_spec)

        # Make request
        response = client.put(
            "/api/spec/test-spec-id", json={"spec": api_spec.model_dump()}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "spec" in data
        assert data["spec"]["topic"] == "Advanced Python"

        # Verify service was called
        mock_services["spec_service"].update_spec.assert_called_once()

    def test_update_spec_not_found(self, client, mock_services, sample_spec):
        """Test updating non-existent spec."""
        # Setup mock to raise KeyError
        mock_services["spec_service"].update_spec.side_effect = KeyError(
            "Spec not found: invalid-id"
        )

        # Convert to API format for request
        api_spec = doc_spec_to_api(sample_spec)

        # Make request
        response = client.put(
            "/api/spec/invalid-id", json={"spec": api_spec.model_dump()}
        )

        # Should return 404
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "not found" in response.json()["detail"].lower()

    def test_update_spec_empty_id(self, client, mock_services, sample_spec):
        """Test updating spec with empty ID."""
        # Convert to API format for request
        api_spec = doc_spec_to_api(sample_spec)

        # Make request with empty ID (URL encoded space)
        response = client.put("/api/spec/%20", json={"spec": api_spec.model_dump()})

        # Should return 400 for empty ID
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_update_spec_empty_topic(self, client, mock_services):
        """Test updating spec with empty topic."""
        # Create spec with empty topic
        spec_data = {"topic": "", "knowledge_units": []}

        # Make request
        response = client.put("/api/spec/test-id", json={"spec": spec_data})

        # Should return 400 for empty topic
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "topic" in response.json()["detail"].lower()

    def test_update_spec_invalid_data(self, client, mock_services):
        """Test updating spec with invalid data."""
        # Make request with invalid spec data
        response = client.put("/api/spec/test-id", json={"spec": {"invalid": "data"}})

        # FastAPI should return 422 for validation error
        assert response.status_code == 422

    def test_update_spec_missing_spec_field(self, client, mock_services):
        """Test updating spec without spec field."""
        response = client.put("/api/spec/test-id", json={})

        # FastAPI should return 422 for missing required field
        assert response.status_code == 422

    def test_update_spec_service_error(self, client, mock_services, sample_spec):
        """Test update spec when service raises unexpected error."""
        # Setup mock to raise exception
        mock_services["spec_service"].update_spec.side_effect = Exception(
            "Storage error"
        )

        # Convert to API format for request
        api_spec = doc_spec_to_api(sample_spec)

        # Make request
        response = client.put("/api/spec/test-id", json={"spec": api_spec.model_dump()})

        # Should return 500
        assert response.status_code == 500


class TestHTTPStatusCodes:
    """Tests to verify correct HTTP status codes are returned."""

    def test_success_returns_200(self, client, mock_services, sample_spec):
        """Test that successful operations return 200."""
        mock_services["spec_service"].generate_spec.return_value = ("id", sample_spec)
        mock_services["spec_service"].get_spec.return_value = sample_spec
        mock_services["spec_service"].update_spec.return_value = sample_spec

        # Test POST
        response = client.post("/api/spec/generate", json={"topic": "Test"})
        assert response.status_code == 200

        # Test GET
        response = client.get("/api/spec/test-id")
        assert response.status_code == 200

        # Test PUT - convert to API format
        api_spec = doc_spec_to_api(sample_spec)
        response = client.put("/api/spec/test-id", json={"spec": api_spec.model_dump()})
        assert response.status_code == 200

    def test_not_found_returns_404(self, client, mock_services):
        """Test that missing resources return 404."""
        mock_services["spec_service"].get_spec.side_effect = KeyError("Not found")
        mock_services["spec_service"].update_spec.side_effect = KeyError("Not found")

        # Test GET
        response = client.get("/api/spec/invalid-id")
        assert response.status_code == 404

        # Test PUT
        response = client.put(
            "/api/spec/invalid-id",
            json={"spec": {"topic": "Test", "knowledge_units": []}},
        )
        assert response.status_code == 404

    def test_server_error_returns_500(self, client, mock_services):
        """Test that unexpected errors return 500."""
        mock_services["spec_service"].generate_spec.side_effect = Exception("Error")
        mock_services["spec_service"].get_spec.side_effect = Exception("Error")
        mock_services["spec_service"].update_spec.side_effect = Exception("Error")

        # Test POST
        response = client.post("/api/spec/generate", json={"topic": "Test"})
        assert response.status_code == 500

        # Test GET
        response = client.get("/api/spec/test-id")
        assert response.status_code == 500

        # Test PUT
        response = client.put(
            "/api/spec/test-id", json={"spec": {"topic": "Test", "knowledge_units": []}}
        )
        assert response.status_code == 500


class TestErrorResponseFormat:
    """Tests to verify consistent error response format."""

    def test_404_error_format(self, client, mock_services):
        """Test that 404 errors have consistent format."""
        mock_services["spec_service"].get_spec.side_effect = KeyError("Not found")

        response = client.get("/api/spec/invalid-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

    def test_500_error_format(self, client, mock_services):
        """Test that 500 errors have consistent format."""
        mock_services["spec_service"].generate_spec.side_effect = Exception(
            "Internal error"
        )

        response = client.post("/api/spec/generate", json={"topic": "Test"})

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
