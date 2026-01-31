"""Service for spec generation and management."""

from typing import Dict, Tuple, List
import uuid
import json
import hashlib
from pathlib import Path
from datetime import datetime
from vividoc.core.models import DocumentSpec, KnowledgeUnitSpec
from vividoc.core.planner import Planner


class SpecService:
    """Handles spec generation and CRUD operations with local file persistence."""

    def __init__(self, planner: Planner, storage_base_dir: str = "outputs"):
        """
        Initialize the spec service.

        Args:
            planner: ViviDoc Planner instance for spec generation
            storage_base_dir: Base directory to store spec folders (relative to project root)
        """
        self.planner = planner
        self.specs: Dict[str, DocumentSpec] = {}
        self.spec_metadata: Dict[str, dict] = {}  # Store topic and time

        # Use absolute path from project root (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent.parent
        self.storage_base_dir = project_root / storage_base_dir
        self.storage_base_dir.mkdir(parents=True, exist_ok=True)

        # Load existing specs from disk
        self._load_specs_from_disk()

    def _topic_to_uuid(self, topic: str) -> str:
        """Generate deterministic UUID from topic using MD5 hash."""
        # Use MD5 hash of topic to generate UUID
        hash_obj = hashlib.md5(topic.encode("utf-8"))
        return str(uuid.UUID(hash_obj.hexdigest()))

    def _get_spec_dir(self, topic_uuid: str) -> Path:
        """Get the directory path for a spec."""
        return self.storage_base_dir / topic_uuid

    def _load_specs_from_disk(self):
        """Load all specs from disk into memory."""
        for spec_dir in self.storage_base_dir.iterdir():
            if spec_dir.is_dir():
                spec_file = spec_dir / "spec.json"
                if spec_file.exists():
                    try:
                        with open(spec_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            spec = DocumentSpec(**data["spec"])
                            spec_id = data["spec_id"]
                            self.specs[spec_id] = spec
                            self.spec_metadata[spec_id] = {
                                "topic": data.get("topic", spec.topic),
                                "time": data.get("time", datetime.now().isoformat()),
                            }
                    except Exception as e:
                        print(f"Warning: Failed to load spec from {spec_file}: {e}")

    def _save_spec_to_disk(self, spec_id: str, spec: DocumentSpec, topic: str):
        """Save a spec to disk in outputs/uuid/ directory."""
        topic_uuid = self._topic_to_uuid(topic)
        spec_dir = self._get_spec_dir(topic_uuid)
        spec_dir.mkdir(parents=True, exist_ok=True)

        spec_file = spec_dir / "spec.json"
        data = {
            "spec_id": spec_id,
            "topic": topic,
            "time": datetime.now().isoformat(),
            "spec": spec.model_dump(),
        }

        with open(spec_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Update metadata
        self.spec_metadata[spec_id] = {"topic": topic, "time": data["time"]}

    def _delete_spec_from_disk(self, spec_id: str):
        """Delete a spec directory from disk."""
        if spec_id in self.spec_metadata:
            topic = self.spec_metadata[spec_id]["topic"]
            topic_uuid = self._topic_to_uuid(topic)
            spec_dir = self._get_spec_dir(topic_uuid)
            if spec_dir.exists():
                import shutil

                shutil.rmtree(spec_dir)

    def generate_spec(self, topic: str) -> Tuple[str, DocumentSpec]:
        """
        Generate spec using Planner, return spec_id and spec.
        Saves to outputs/uuid/ directory where uuid is derived from topic.

        Args:
            topic: Topic for document generation

        Returns:
            Tuple of (spec_id, DocumentSpec)
        """
        # Generate spec using Planner
        spec = self.planner.run(topic)

        # Generate spec ID from topic (deterministic)
        spec_id = self._topic_to_uuid(topic)

        # Store spec in memory and disk
        self.specs[spec_id] = spec
        self._save_spec_to_disk(spec_id, spec, topic)

        return spec_id, spec

    def get_spec(self, spec_id: str) -> DocumentSpec:
        """
        Retrieve spec by ID.

        Args:
            spec_id: Spec identifier

        Returns:
            DocumentSpec object

        Raises:
            KeyError: If spec_id not found
        """
        if spec_id not in self.specs:
            raise KeyError(f"Spec not found: {spec_id}")

        return self.specs[spec_id]

    def update_spec(self, spec_id: str, spec: DocumentSpec) -> DocumentSpec:
        """
        Update existing spec and save to disk.

        Args:
            spec_id: Spec identifier
            spec: Updated DocumentSpec

        Returns:
            Updated DocumentSpec

        Raises:
            KeyError: If spec_id not found
        """
        if spec_id not in self.specs:
            raise KeyError(f"Spec not found: {spec_id}")

        # Get topic from metadata
        topic = self.spec_metadata.get(spec_id, {}).get("topic", spec.topic)

        self.specs[spec_id] = spec
        self._save_spec_to_disk(spec_id, spec, topic)
        return spec

    def delete_ku(self, spec_id: str, ku_index: int) -> DocumentSpec:
        """
        Delete knowledge unit from spec and save to disk.

        Args:
            spec_id: Spec identifier
            ku_index: Index of knowledge unit to delete

        Returns:
            Updated DocumentSpec

        Raises:
            KeyError: If spec_id not found
            IndexError: If ku_index is out of range
        """
        if spec_id not in self.specs:
            raise KeyError(f"Spec not found: {spec_id}")

        spec = self.specs[spec_id]
        topic = self.spec_metadata.get(spec_id, {}).get("topic", spec.topic)

        if ku_index < 0 or ku_index >= len(spec.knowledge_units):
            raise IndexError(f"Knowledge unit index out of range: {ku_index}")

        # Create new list without the deleted KU
        updated_kus = [ku for i, ku in enumerate(spec.knowledge_units) if i != ku_index]

        # Create updated spec
        updated_spec = DocumentSpec(topic=spec.topic, knowledge_units=updated_kus)

        self.specs[spec_id] = updated_spec
        self._save_spec_to_disk(spec_id, updated_spec, topic)
        return updated_spec

    def add_ku(
        self, spec_id: str, ku: KnowledgeUnitSpec, position: int
    ) -> DocumentSpec:
        """
        Add knowledge unit to spec at position and save to disk.

        Args:
            spec_id: Spec identifier
            ku: KnowledgeUnitSpec to add
            position: Position to insert the KU (0-indexed)

        Returns:
            Updated DocumentSpec

        Raises:
            KeyError: If spec_id not found
            ValueError: If position is invalid
        """
        if spec_id not in self.specs:
            raise KeyError(f"Spec not found: {spec_id}")

        spec = self.specs[spec_id]
        topic = self.spec_metadata.get(spec_id, {}).get("topic", spec.topic)

        if position < 0 or position > len(spec.knowledge_units):
            raise ValueError(
                f"Invalid position: {position}. Must be between 0 and {len(spec.knowledge_units)}"
            )

        # Create new list with KU inserted at position
        updated_kus = list(spec.knowledge_units)
        updated_kus.insert(position, ku)

        # Create updated spec
        updated_spec = DocumentSpec(topic=spec.topic, knowledge_units=updated_kus)

        self.specs[spec_id] = updated_spec
        self._save_spec_to_disk(spec_id, updated_spec, topic)
        return updated_spec

    def reorder_kus(self, spec_id: str, new_order: List[int]) -> DocumentSpec:
        """
        Reorder knowledge units and save to disk.

        Args:
            spec_id: Spec identifier
            new_order: List of indices representing the new order
                      (e.g., [2, 0, 1] means move KU at index 2 to position 0,
                       KU at index 0 to position 1, and KU at index 1 to position 2)

        Returns:
            Updated DocumentSpec

        Raises:
            KeyError: If spec_id not found
            ValueError: If new_order is invalid
        """
        if spec_id not in self.specs:
            raise KeyError(f"Spec not found: {spec_id}")

        spec = self.specs[spec_id]
        topic = self.spec_metadata.get(spec_id, {}).get("topic", spec.topic)

        # Validate new_order
        if len(new_order) != len(spec.knowledge_units):
            raise ValueError(
                f"new_order length ({len(new_order)}) must match "
                f"number of knowledge units ({len(spec.knowledge_units)})"
            )

        if sorted(new_order) != list(range(len(spec.knowledge_units))):
            raise ValueError(
                f"new_order must be a permutation of indices 0 to {len(spec.knowledge_units) - 1}"
            )

        # Reorder knowledge units
        updated_kus = [spec.knowledge_units[i] for i in new_order]

        # Create updated spec
        updated_spec = DocumentSpec(topic=spec.topic, knowledge_units=updated_kus)

        self.specs[spec_id] = updated_spec
        self._save_spec_to_disk(spec_id, updated_spec, topic)
        return updated_spec
