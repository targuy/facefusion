"""Type definitions for the repository system."""

from typing import Any, Dict, List, TypedDict


class PersonEntry(TypedDict):
	"""Person entry in the repository."""
	person_id: str
	display_name: str
	face_paths: List[str]
	face_count: int
	metadata: Dict[str, Any]


class RepositoryStorage(TypedDict):
	"""Repository storage structure."""
	version: str
	persons: Dict[str, PersonEntry]
