"""Person-centric face management for FaceFusion Repository"""

import hashlib
import uuid
from datetime import datetime
from typing import List, Optional

from facefusion_repository.storage.file_manager import FileManager
from facefusion_repository.storage.json_storage import JsonStorage
from facefusion_repository.types import OperationResult, PersonFace, RepositoryEntry


class PersonManager:
	"""Manages person entities and their associated faces"""
	
	def __init__(self, repository_path : str = '.facefusion_repository'):
		self.storage = JsonStorage(repository_path)
		self.file_manager = FileManager(repository_path)
	
	def init_repository(self) -> OperationResult:
		"""Initialize the repository"""
		success = self.storage.init_repository()
		return\
		{
			'success': success,
			'message': 'Repository initialized successfully' if success else 'Failed to initialize repository',
			'data': None
		}
	
	def repository_exists(self) -> bool:
		"""Check if repository is initialized"""
		return self.storage.repository_exists()
	
	def add_person(self, person_name : str, person_id : Optional[str] = None) -> OperationResult:
		"""Add a new person to the repository"""
		if not self.repository_exists():
			return\
			{
				'success': False,
				'message': 'Repository not initialized. Run repo-init first.',
				'data': None
			}
		
		if not person_id:
			person_id = self._generate_person_id(person_name)
		
		success = self.storage.add_person(person_id, person_name)
		
		if success:
			return\
			{
				'success': True,
				'message': f'Person "{person_name}" added successfully',
				'data': {'person_id': person_id}
			}
		return\
		{
			'success': False,
			'message': f'Person "{person_name}" already exists or error occurred',
			'data': None
		}
	
	def get_person(self, person_id : str) -> Optional[RepositoryEntry]:
		"""Get person entry by ID"""
		return self.storage.get_person(person_id)
	
	def list_persons(self) -> List[RepositoryEntry]:
		"""List all persons in repository"""
		return self.storage.list_persons()
	
	def remove_person(self, person_id : str) -> OperationResult:
		"""Remove a person and their faces from repository"""
		if not self.repository_exists():
			return\
			{
				'success': False,
				'message': 'Repository not initialized',
				'data': None
			}
		
		# Remove files
		self.file_manager.remove_person_files(person_id)
		
		# Remove from database
		success = self.storage.remove_person(person_id)
		
		if success:
			return\
			{
				'success': True,
				'message': f'Person "{person_id}" removed successfully',
				'data': None
			}
		return\
		{
			'success': False,
			'message': f'Failed to remove person "{person_id}"',
			'data': None
		}
	
	def add_face_to_person(self, person_id : str, face_data : PersonFace) -> OperationResult:
		"""Add a face to a person's collection"""
		if not self.repository_exists():
			return\
			{
				'success': False,
				'message': 'Repository not initialized',
				'data': None
			}
		
		person = self.get_person(person_id)
		if not person:
			return\
			{
				'success': False,
				'message': f'Person "{person_id}" not found',
				'data': None
			}
		
		success = self.storage.add_face_to_person(person_id, face_data)
		
		if success:
			return\
			{
				'success': True,
				'message': f'Face added to person "{person_id}"',
				'data': {'face_id': face_data['face_id']}
			}
		return\
		{
			'success': False,
			'message': f'Failed to add face to person "{person_id}"',
			'data': None
		}
	
	def get_faces_for_person(self, person_id : str) -> List[PersonFace]:
		"""Get all faces for a person"""
		return self.storage.get_faces_for_person(person_id)
	
	def _generate_person_id(self, person_name : str) -> str:
		"""Generate a unique person ID from name"""
		base_id = person_name.lower().replace(' ', '_')
		hash_suffix = hashlib.md5(f"{person_name}{uuid.uuid4()}".encode()).hexdigest()[:8]
		return f"{base_id}_{hash_suffix}"
	
	def get_best_face_for_person(self, person_id : str) -> Optional[PersonFace]:
		"""Get the best quality face for a person"""
		faces = self.get_faces_for_person(person_id)
		if not faces:
			return None
		
		# Sort by overall quality score
		sorted_faces = sorted(faces, key=lambda f: f['quality']['overall_quality'], reverse=True)
		return sorted_faces[0]
