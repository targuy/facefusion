"""Face selector for repository-based face selection."""

from typing import List, Optional

from facefusion_repository.manager import RepositoryManager


class RepositorySelector:
	"""Selects faces from repository for processing."""

	def __init__(self, repository_manager: RepositoryManager):
		self.manager = repository_manager

	def get_person_faces(self, person_name: str) -> List[str]:
		"""Get all face paths for a person by name."""
		person = self.manager.get_person_by_name(person_name)
		if person:
			return person['face_paths']
		return []

	def get_best_person_face(self, person_name: str) -> Optional[str]:
		"""Get the best face for a person (first face for now)."""
		face_paths = self.get_person_faces(person_name)
		if face_paths:
			return face_paths[0]
		return None

	def select_faces_for_person(self, person_name: str, fallback_persons: Optional[List[str]] = None) -> List[str]:
		"""
		Select faces for a person with optional fallback chain.
		
		Args:
			person_name: Primary person name
			fallback_persons: Optional list of fallback person names
		
		Returns:
			List of face paths to use as source faces
		"""
		# Try primary person
		face_paths = self.get_person_faces(person_name)
		if face_paths:
			return face_paths
		
		# Try fallback persons
		if fallback_persons:
			for fallback_name in fallback_persons:
				face_paths = self.get_person_faces(fallback_name)
				if face_paths:
					return face_paths
		
		return []
