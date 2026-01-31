"""Tests for SpecService class."""

import pytest
from unittest.mock import Mock
from vividoc.core.models import DocumentSpec, KnowledgeUnitSpec
from vividoc.entrypoint.services.spec_service import SpecService


@pytest.fixture
def mock_planner():
    """Create a mock Planner."""
    planner = Mock()
    return planner


@pytest.fixture
def spec_service(mock_planner):
    """Create a SpecService instance with mock planner."""
    return SpecService(mock_planner)


@pytest.fixture
def sample_ku():
    """Create a sample KnowledgeUnitSpec."""
    return KnowledgeUnitSpec(
        id="ku_1",
        unit_content="Sample content",
        text_description="Text description",
        interaction_description="Interaction description",
    )


@pytest.fixture
def sample_spec():
    """Create a sample DocumentSpec."""
    return DocumentSpec(
        topic="Test Topic",
        knowledge_units=[
            KnowledgeUnitSpec(
                id="ku_1",
                unit_content="First KU",
                text_description="First text",
                interaction_description="First interaction",
            ),
            KnowledgeUnitSpec(
                id="ku_2",
                unit_content="Second KU",
                text_description="Second text",
                interaction_description="Second interaction",
            ),
            KnowledgeUnitSpec(
                id="ku_3",
                unit_content="Third KU",
                text_description="Third text",
                interaction_description="Third interaction",
            ),
        ],
    )


class TestSpecServiceGeneration:
    """Tests for spec generation."""

    def test_generate_spec_returns_id_and_spec(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that generate_spec returns both spec_id and spec."""
        # Arrange
        mock_planner.run.return_value = sample_spec

        # Act
        spec_id, spec = spec_service.generate_spec("Test Topic")

        # Assert
        assert spec_id is not None
        assert isinstance(spec_id, str)
        assert len(spec_id) > 0
        assert spec == sample_spec
        mock_planner.run.assert_called_once_with("Test Topic")

    def test_generate_spec_stores_spec(self, spec_service, mock_planner, sample_spec):
        """Test that generate_spec stores the spec in memory."""
        # Arrange
        mock_planner.run.return_value = sample_spec

        # Act
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Assert
        assert spec_id in spec_service.specs
        assert spec_service.specs[spec_id] == sample_spec

    def test_generate_spec_unique_ids(self, spec_service, mock_planner, sample_spec):
        """Test that generate_spec creates unique IDs for different specs."""
        # Arrange
        mock_planner.run.return_value = sample_spec

        # Act
        spec_id_1, _ = spec_service.generate_spec("Topic 1")
        spec_id_2, _ = spec_service.generate_spec("Topic 2")

        # Assert
        assert spec_id_1 != spec_id_2


class TestSpecServiceRetrieval:
    """Tests for spec retrieval."""

    def test_get_spec_returns_stored_spec(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that get_spec returns the correct spec."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, original_spec = spec_service.generate_spec("Test Topic")

        # Act
        retrieved_spec = spec_service.get_spec(spec_id)

        # Assert
        assert retrieved_spec == original_spec

    def test_get_spec_raises_keyerror_for_invalid_id(self, spec_service):
        """Test that get_spec raises KeyError for non-existent spec_id."""
        # Act & Assert
        with pytest.raises(KeyError, match="Spec not found"):
            spec_service.get_spec("invalid_id")


class TestSpecServiceUpdate:
    """Tests for spec updates."""

    def test_update_spec_modifies_stored_spec(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that update_spec modifies the stored spec."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Modify the spec
        modified_spec = DocumentSpec(
            topic="Modified Topic", knowledge_units=sample_spec.knowledge_units
        )

        # Act
        result = spec_service.update_spec(spec_id, modified_spec)

        # Assert
        assert result == modified_spec
        assert spec_service.specs[spec_id] == modified_spec
        assert spec_service.specs[spec_id].topic == "Modified Topic"

    def test_update_spec_raises_keyerror_for_invalid_id(self, spec_service):
        """Test that update_spec raises KeyError for non-existent spec_id."""
        # Arrange
        spec = DocumentSpec(topic="Test", knowledge_units=[])

        # Act & Assert
        with pytest.raises(KeyError, match="Spec not found"):
            spec_service.update_spec("invalid_id", spec)


class TestSpecServiceDeleteKU:
    """Tests for deleting knowledge units."""

    def test_delete_ku_removes_target(self, spec_service, mock_planner, sample_spec):
        """Test that delete_ku removes the specified KU."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        original_count = len(sample_spec.knowledge_units)

        # Act
        updated_spec = spec_service.delete_ku(spec_id, 1)

        # Assert
        assert len(updated_spec.knowledge_units) == original_count - 1
        assert updated_spec.knowledge_units[0].id == "ku_1"
        assert updated_spec.knowledge_units[1].id == "ku_3"
        # Verify ku_2 is not in the list
        assert all(ku.id != "ku_2" for ku in updated_spec.knowledge_units)

    def test_delete_ku_first_element(self, spec_service, mock_planner, sample_spec):
        """Test deleting the first KU."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Act
        updated_spec = spec_service.delete_ku(spec_id, 0)

        # Assert
        assert len(updated_spec.knowledge_units) == 2
        assert updated_spec.knowledge_units[0].id == "ku_2"
        assert updated_spec.knowledge_units[1].id == "ku_3"

    def test_delete_ku_last_element(self, spec_service, mock_planner, sample_spec):
        """Test deleting the last KU."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Act
        updated_spec = spec_service.delete_ku(spec_id, 2)

        # Assert
        assert len(updated_spec.knowledge_units) == 2
        assert updated_spec.knowledge_units[0].id == "ku_1"
        assert updated_spec.knowledge_units[1].id == "ku_2"

    def test_delete_ku_raises_keyerror_for_invalid_spec_id(self, spec_service):
        """Test that delete_ku raises KeyError for non-existent spec_id."""
        # Act & Assert
        with pytest.raises(KeyError, match="Spec not found"):
            spec_service.delete_ku("invalid_id", 0)

    def test_delete_ku_raises_indexerror_for_invalid_index(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that delete_ku raises IndexError for out-of-range index."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Act & Assert
        with pytest.raises(IndexError, match="Knowledge unit index out of range"):
            spec_service.delete_ku(spec_id, 10)

    def test_delete_ku_raises_indexerror_for_negative_index(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that delete_ku raises IndexError for negative index."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Act & Assert
        with pytest.raises(IndexError, match="Knowledge unit index out of range"):
            spec_service.delete_ku(spec_id, -1)


class TestSpecServiceAddKU:
    """Tests for adding knowledge units."""

    def test_add_ku_at_beginning(
        self, spec_service, mock_planner, sample_spec, sample_ku
    ):
        """Test adding a KU at the beginning."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_ku = KnowledgeUnitSpec(
            id="ku_new",
            unit_content="New KU",
            text_description="New text",
            interaction_description="New interaction",
        )

        # Act
        updated_spec = spec_service.add_ku(spec_id, new_ku, 0)

        # Assert
        assert len(updated_spec.knowledge_units) == 4
        assert updated_spec.knowledge_units[0].id == "ku_new"
        assert updated_spec.knowledge_units[1].id == "ku_1"
        assert updated_spec.knowledge_units[2].id == "ku_2"
        assert updated_spec.knowledge_units[3].id == "ku_3"

    def test_add_ku_in_middle(self, spec_service, mock_planner, sample_spec):
        """Test adding a KU in the middle."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_ku = KnowledgeUnitSpec(
            id="ku_new",
            unit_content="New KU",
            text_description="New text",
            interaction_description="New interaction",
        )

        # Act
        updated_spec = spec_service.add_ku(spec_id, new_ku, 2)

        # Assert
        assert len(updated_spec.knowledge_units) == 4
        assert updated_spec.knowledge_units[0].id == "ku_1"
        assert updated_spec.knowledge_units[1].id == "ku_2"
        assert updated_spec.knowledge_units[2].id == "ku_new"
        assert updated_spec.knowledge_units[3].id == "ku_3"

    def test_add_ku_at_end(self, spec_service, mock_planner, sample_spec):
        """Test adding a KU at the end."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_ku = KnowledgeUnitSpec(
            id="ku_new",
            unit_content="New KU",
            text_description="New text",
            interaction_description="New interaction",
        )

        # Act
        updated_spec = spec_service.add_ku(spec_id, new_ku, 3)

        # Assert
        assert len(updated_spec.knowledge_units) == 4
        assert updated_spec.knowledge_units[0].id == "ku_1"
        assert updated_spec.knowledge_units[1].id == "ku_2"
        assert updated_spec.knowledge_units[2].id == "ku_3"
        assert updated_spec.knowledge_units[3].id == "ku_new"

    def test_add_ku_raises_keyerror_for_invalid_spec_id(self, spec_service, sample_ku):
        """Test that add_ku raises KeyError for non-existent spec_id."""
        # Act & Assert
        with pytest.raises(KeyError, match="Spec not found"):
            spec_service.add_ku("invalid_id", sample_ku, 0)

    def test_add_ku_raises_valueerror_for_invalid_position(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that add_ku raises ValueError for invalid position."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_ku = KnowledgeUnitSpec(
            id="ku_new",
            unit_content="New KU",
            text_description="New text",
            interaction_description="New interaction",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid position"):
            spec_service.add_ku(spec_id, new_ku, 10)

    def test_add_ku_raises_valueerror_for_negative_position(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that add_ku raises ValueError for negative position."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_ku = KnowledgeUnitSpec(
            id="ku_new",
            unit_content="New KU",
            text_description="New text",
            interaction_description="New interaction",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid position"):
            spec_service.add_ku(spec_id, new_ku, -1)


class TestSpecServiceReorderKUs:
    """Tests for reordering knowledge units."""

    def test_reorder_kus_preserves_content(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that reorder_kus preserves all KU content."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_order = [2, 0, 1]  # Move ku_3 to front, ku_1 to middle, ku_2 to end

        # Act
        updated_spec = spec_service.reorder_kus(spec_id, new_order)

        # Assert
        assert len(updated_spec.knowledge_units) == 3
        assert updated_spec.knowledge_units[0].id == "ku_3"
        assert updated_spec.knowledge_units[0].unit_content == "Third KU"
        assert updated_spec.knowledge_units[1].id == "ku_1"
        assert updated_spec.knowledge_units[1].unit_content == "First KU"
        assert updated_spec.knowledge_units[2].id == "ku_2"
        assert updated_spec.knowledge_units[2].unit_content == "Second KU"

    def test_reorder_kus_reverse_order(self, spec_service, mock_planner, sample_spec):
        """Test reversing the order of KUs."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_order = [2, 1, 0]

        # Act
        updated_spec = spec_service.reorder_kus(spec_id, new_order)

        # Assert
        assert updated_spec.knowledge_units[0].id == "ku_3"
        assert updated_spec.knowledge_units[1].id == "ku_2"
        assert updated_spec.knowledge_units[2].id == "ku_1"

    def test_reorder_kus_identity_order(self, spec_service, mock_planner, sample_spec):
        """Test reordering with identity permutation (no change)."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_order = [0, 1, 2]

        # Act
        updated_spec = spec_service.reorder_kus(spec_id, new_order)

        # Assert
        assert updated_spec.knowledge_units[0].id == "ku_1"
        assert updated_spec.knowledge_units[1].id == "ku_2"
        assert updated_spec.knowledge_units[2].id == "ku_3"

    def test_reorder_kus_raises_keyerror_for_invalid_spec_id(self, spec_service):
        """Test that reorder_kus raises KeyError for non-existent spec_id."""
        # Act & Assert
        with pytest.raises(KeyError, match="Spec not found"):
            spec_service.reorder_kus("invalid_id", [0, 1, 2])

    def test_reorder_kus_raises_valueerror_for_wrong_length(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that reorder_kus raises ValueError for wrong length."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Act & Assert
        with pytest.raises(ValueError, match="new_order length"):
            spec_service.reorder_kus(spec_id, [0, 1])

    def test_reorder_kus_raises_valueerror_for_invalid_permutation(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that reorder_kus raises ValueError for invalid permutation."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Act & Assert - duplicate indices
        with pytest.raises(ValueError, match="must be a permutation"):
            spec_service.reorder_kus(spec_id, [0, 0, 1])

        # Act & Assert - out of range indices
        with pytest.raises(ValueError, match="must be a permutation"):
            spec_service.reorder_kus(spec_id, [0, 1, 5])


class TestSpecServiceRoundTrip:
    """Tests for spec modification round-trip property."""

    def test_update_then_retrieve_returns_modified_spec(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that updating then retrieving returns the modified spec."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Modify by updating topic
        modified_spec = DocumentSpec(
            topic="Modified Topic", knowledge_units=sample_spec.knowledge_units
        )

        # Act
        spec_service.update_spec(spec_id, modified_spec)
        retrieved_spec = spec_service.get_spec(spec_id)

        # Assert
        assert retrieved_spec == modified_spec
        assert retrieved_spec.topic == "Modified Topic"

    def test_delete_ku_then_retrieve_returns_modified_spec(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that deleting a KU then retrieving returns the modified spec."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Act
        spec_service.delete_ku(spec_id, 1)
        retrieved_spec = spec_service.get_spec(spec_id)

        # Assert
        assert len(retrieved_spec.knowledge_units) == 2
        assert retrieved_spec.knowledge_units[0].id == "ku_1"
        assert retrieved_spec.knowledge_units[1].id == "ku_3"

    def test_add_ku_then_retrieve_returns_modified_spec(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that adding a KU then retrieving returns the modified spec."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")
        new_ku = KnowledgeUnitSpec(
            id="ku_new",
            unit_content="New KU",
            text_description="New text",
            interaction_description="New interaction",
        )

        # Act
        spec_service.add_ku(spec_id, new_ku, 1)
        retrieved_spec = spec_service.get_spec(spec_id)

        # Assert
        assert len(retrieved_spec.knowledge_units) == 4
        assert retrieved_spec.knowledge_units[1].id == "ku_new"

    def test_reorder_kus_then_retrieve_returns_modified_spec(
        self, spec_service, mock_planner, sample_spec
    ):
        """Test that reordering KUs then retrieving returns the modified spec."""
        # Arrange
        mock_planner.run.return_value = sample_spec
        spec_id, _ = spec_service.generate_spec("Test Topic")

        # Act
        spec_service.reorder_kus(spec_id, [2, 0, 1])
        retrieved_spec = spec_service.get_spec(spec_id)

        # Assert
        assert retrieved_spec.knowledge_units[0].id == "ku_3"
        assert retrieved_spec.knowledge_units[1].id == "ku_1"
        assert retrieved_spec.knowledge_units[2].id == "ku_2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
