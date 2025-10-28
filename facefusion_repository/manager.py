"""Manager for repository operations."""

import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.storage import Storage
from facefusion_repository.types import PersonEntry


class RepositoryManager:
	"""High-level manager for repository operations."""

	def __init__(self, repository_path: str = None):
		if repository_path is None:
			repository_path = '.face_repository'
		self.storage = Storage(repository_path)

	def create_person(self, display_name: str, face_paths: List[str]) -> PersonEntry:
		"""Create a new person in the repository."""
		person_id = str(uuid.uuid4())
		
		# Copy face images to repository
		person_face_dir = self.storage.get_person_face_dir(person_id)
		stored_face_paths = []
		
		for face_path in face_paths:
			if Path(face_path).exists():
				dest_path = person_face_dir / Path(face_path).name
				shutil.copy2(face_path, dest_path)
				stored_face_paths.append(str(dest_path))
		
		person: PersonEntry = {
			'person_id': person_id,
			'display_name': display_name,
			'face_paths': stored_face_paths,
			'face_count': len(stored_face_paths),
			'metadata': {}
		}
		
		self.storage.add_person(person)
		return person

	def get_person(self, person_id: str) -> Optional[PersonEntry]:
		"""Get a person by ID."""
		return self.storage.get_person(person_id)

	def get_person_by_name(self, display_name: str) -> Optional[PersonEntry]:
		"""Get a person by display name."""
		persons = self.storage.get_all_persons()
		for person in persons.values():
			if person['display_name'] == display_name:
				return person
		return None

	def list_persons(self) -> List[PersonEntry]:
		"""List all persons in the repository."""
		persons = self.storage.get_all_persons()
		return list(persons.values())

	def remove_person(self, person_id: str) -> bool:
		"""Remove a person from the repository."""
		person = self.storage.get_person(person_id)
		if person:
			# Remove face files
			person_face_dir = self.storage.get_person_face_dir(person_id)
			if person_face_dir.exists():
				shutil.rmtree(person_face_dir)
			
			# Remove from storage
			return self.storage.remove_person(person_id)
		return False

	def add_faces_to_person(self, person_id: str, face_paths: List[str]) -> bool:
		"""Add more faces to an existing person."""
		person = self.storage.get_person(person_id)
		if not person:
			return False
		
		person_face_dir = self.storage.get_person_face_dir(person_id)
		stored_face_paths = list(person['face_paths'])
		
		for face_path in face_paths:
			if Path(face_path).exists():
				dest_path = person_face_dir / Path(face_path).name
				shutil.copy2(face_path, dest_path)
				stored_face_paths.append(str(dest_path))
		
		return self.storage.update_person(person_id, {
			'face_paths': stored_face_paths,
			'face_count': len(stored_face_paths)
		})
