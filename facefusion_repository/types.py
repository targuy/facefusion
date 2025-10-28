"""
Type definitions for the FaceFusion Repository system.
"""

from typing import Dict, List, TypedDict


class FaceEntry(TypedDict):
	"""Represents a single face entry in the repository."""
	path: str
	embedding: List[float]
	quality_score: float
	added_date: str


class PersonEntry(TypedDict):
	"""Represents a person in the repository with their associated faces."""
	name: str
	faces: List[FaceEntry]
	created_date: str
	updated_date: str


class RepositoryData(TypedDict):
	"""Main repository data structure."""
	version: str
	persons: Dict[str, PersonEntry]
