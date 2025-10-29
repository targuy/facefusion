"""Type definitions for the repository system."""

from typing import Any, Dict, List, TypedDict


class QualityMetricsDict(TypedDict, total=False):
	"""Quality metrics for a face."""
	sharpness: float
	brightness: float
	contrast: float
	resolution: float
	overall: float


class PoseMetricsDict(TypedDict, total=False):
	"""Pose metrics for a face (pitch, yaw, roll in degrees)."""
	pitch: float
	yaw: float
	roll: float


class FaceMetadata(TypedDict, total=False):
	"""Metadata for a face in the repository."""
	quality: QualityMetricsDict
	pose: PoseMetricsDict


class PersonEntry(TypedDict):
	"""Person entry in the repository."""
	person_id: str
	display_name: str
	face_paths: List[str]
	face_count: int
	metadata: Dict[str, Any]


class PersonEntryWithMetadata(PersonEntry, total=False):
	"""Person entry with optional face metadata."""
	face_metadata: Dict[str, FaceMetadata]  # Optional: per-face metadata keyed by face path


class RepositoryStorage(TypedDict):
	"""Repository storage structure."""
	version: str
	persons: Dict[str, PersonEntry]
