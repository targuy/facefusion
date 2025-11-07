"""Type definitions for the repository system."""

from typing import Any, Dict, List, Tuple, TypedDict


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


class CoverageZone(TypedDict, total=False):
	"""Coverage zone for a face (angle ranges in 3D space)."""
	pitch_range: Tuple[float, float]  # (min, max) in degrees
	yaw_range: Tuple[float, float]    # (min, max) in degrees
	roll_range: Tuple[float, float]   # (min, max) in degrees


class PreviewResultDict(TypedDict, total=False):
	"""Preview result for a test face."""
	test_face_path: str
	preview_path: str
	quality_score: float
	success: bool
	message: str


class FaceMetadata(TypedDict, total=False):
	"""Metadata for a face in the repository."""
	quality: QualityMetricsDict
	pose: PoseMetricsDict
	coverage_zones: List[CoverageZone]
	preview_results: Dict[str, PreviewResultDict]  # test_face_path -> result


class PersonEntry(TypedDict):
	"""Person entry in the repository."""
	person_id: str
	display_name: str
	normalized_name: str  # Lowercase, stripped version for uniqueness check
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
