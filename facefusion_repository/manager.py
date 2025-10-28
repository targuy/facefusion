"""Manager for repository operations."""

import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.quality_assessor import assess_face_from_path
from facefusion_repository.storage import Storage
from facefusion_repository.types import FaceMetadata, PersonEntry


class RepositoryManager:
	"""High-level manager for repository operations."""

	def __init__(self, repository_path: str = None):
		if repository_path is None:
			repository_path = '.face_repository'
		self.storage = Storage(repository_path)

	def create_person(
		self,
		display_name: str,
		face_paths: List[str],
		quality_threshold: Optional[float] = None,
		assess_quality: bool = True
	) -> PersonEntry:
		"""
		Create a new person in the repository.
		
		Args:
			display_name: Display name for the person
			face_paths: Paths to face images
			quality_threshold: Optional minimum quality threshold (0.0 to 1.0)
			assess_quality: Whether to assess face quality (default: True)
		
		Returns:
			PersonEntry for the created person
		"""
		person_id = str(uuid.uuid4())
		
		# Copy face images to repository
		person_face_dir = self.storage.get_person_face_dir(person_id)
		stored_face_paths = []
		face_metadata: Dict[str, FaceMetadata] = {}
		
		for face_path in face_paths:
			if Path(face_path).exists():
				dest_path = person_face_dir / Path(face_path).name
				shutil.copy2(face_path, dest_path)
				dest_path_str = str(dest_path)
				
				# Assess quality if enabled
				if assess_quality:
					quality_metrics = assess_face_from_path(face_path)
					
					# Check quality threshold
					if quality_threshold is not None and quality_metrics.overall < quality_threshold:
						# Skip this face if below threshold
						continue
					
					# Store quality metrics
					face_metadata[dest_path_str] = {
						'quality': {
							'sharpness': quality_metrics.sharpness,
							'brightness': quality_metrics.brightness,
							'contrast': quality_metrics.contrast,
							'resolution': quality_metrics.resolution,
							'overall': quality_metrics.overall
						}
					}
				
				stored_face_paths.append(dest_path_str)
		
		person: PersonEntry = {
			'person_id': person_id,
			'display_name': display_name,
			'face_paths': stored_face_paths,
			'face_count': len(stored_face_paths),
			'metadata': {},
			'face_metadata': face_metadata if face_metadata else None
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

	def add_faces_to_person(
		self,
		person_id: str,
		face_paths: List[str],
		quality_threshold: Optional[float] = None,
		assess_quality: bool = True
	) -> bool:
		"""
		Add more faces to an existing person.
		
		Args:
			person_id: ID of the person
			face_paths: Paths to face images to add
			quality_threshold: Optional minimum quality threshold (0.0 to 1.0)
			assess_quality: Whether to assess face quality (default: True)
		
		Returns:
			True if successful, False otherwise
		"""
		person = self.storage.get_person(person_id)
		if not person:
			return False
		
		person_face_dir = self.storage.get_person_face_dir(person_id)
		stored_face_paths = list(person['face_paths'])
		face_metadata = dict(person.get('face_metadata') or {})
		
		for face_path in face_paths:
			if Path(face_path).exists():
				dest_path = person_face_dir / Path(face_path).name
				shutil.copy2(face_path, dest_path)
				dest_path_str = str(dest_path)
				
				# Assess quality if enabled
				if assess_quality:
					quality_metrics = assess_face_from_path(face_path)
					
					# Check quality threshold
					if quality_threshold is not None and quality_metrics.overall < quality_threshold:
						# Skip this face if below threshold
						continue
					
					# Store quality metrics
					face_metadata[dest_path_str] = {
						'quality': {
							'sharpness': quality_metrics.sharpness,
							'brightness': quality_metrics.brightness,
							'contrast': quality_metrics.contrast,
							'resolution': quality_metrics.resolution,
							'overall': quality_metrics.overall
						}
					}
				
				stored_face_paths.append(dest_path_str)
		
		return self.storage.update_person(person_id, {
			'face_paths': stored_face_paths,
			'face_count': len(stored_face_paths),
			'face_metadata': face_metadata if face_metadata else None
		})
