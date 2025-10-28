"""
Core repository management functionality.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.types import FaceEntry, PersonEntry, RepositoryData


DEFAULT_REPOSITORY_PATH = '.facefusion_repository'


class RepositoryManager:
	"""Manages the face repository."""
	
	def __init__(self, repository_path: str = DEFAULT_REPOSITORY_PATH) -> None:
		"""Initialize the repository manager.
		
		Args:
			repository_path: Path to the repository directory
		"""
		self.repository_path = Path(repository_path)
		self.data_file = self.repository_path / 'repository.json'
		self.faces_dir = self.repository_path / 'faces'
	
	def initialize(self) -> bool:
		"""Initialize a new repository.
		
		Returns:
			True if successful, False otherwise
		"""
		try:
			# Create directory structure
			self.repository_path.mkdir(parents=True, exist_ok=True)
			self.faces_dir.mkdir(parents=True, exist_ok=True)
			
			# Initialize repository data
			data: RepositoryData = {
				'version': '1.0.0',
				'persons': {}
			}
			
			# Save initial data
			with open(self.data_file, 'w') as f:
				json.dump(data, f, indent=2)
			
			return True
		except Exception:
			return False
	
	def exists(self) -> bool:
		"""Check if repository exists.
		
		Returns:
			True if repository exists, False otherwise
		"""
		return self.data_file.exists()
	
	def load(self) -> Optional[RepositoryData]:
		"""Load repository data.
		
		Returns:
			Repository data or None if failed
		"""
		try:
			with open(self.data_file, 'r') as f:
				return json.load(f)
		except Exception:
			return None
	
	def save(self, data: RepositoryData) -> bool:
		"""Save repository data.
		
		Args:
			data: Repository data to save
			
		Returns:
			True if successful, False otherwise
		"""
		try:
			with open(self.data_file, 'w') as f:
				json.dump(data, f, indent=2)
			return True
		except Exception:
			return False
	
	def add_person(self, person_name: str) -> bool:
		"""Add a new person to the repository.
		
		Args:
			person_name: Name of the person
			
		Returns:
			True if successful, False otherwise
		"""
		data = self.load()
		if data is None:
			return False
		
		if person_name in data['persons']:
			return False  # Person already exists
		
		now = datetime.now().isoformat()
		person_entry: PersonEntry = {
			'name': person_name,
			'faces': [],
			'created_date': now,
			'updated_date': now
		}
		
		data['persons'][person_name] = person_entry
		
		# Create person directory
		person_dir = self.faces_dir / person_name
		person_dir.mkdir(parents=True, exist_ok=True)
		
		return self.save(data)
	
	def add_face(self, person_name: str, face_path: str, embedding: List[float], quality_score: float = 0.0) -> bool:
		"""Add a face to a person in the repository.
		
		Args:
			person_name: Name of the person
			face_path: Path to the face image
			embedding: Face embedding vector
			quality_score: Quality score of the face
			
		Returns:
			True if successful, False otherwise
		"""
		data = self.load()
		if data is None:
			return False
		
		if person_name not in data['persons']:
			# Create person if doesn't exist
			if not self.add_person(person_name):
				return False
			data = self.load()
			if data is None:
				return False
		
		# Copy face image to repository
		person_dir = self.faces_dir / person_name
		face_filename = Path(face_path).name
		dest_path = person_dir / face_filename
		
		# Copy file
		import shutil
		try:
			shutil.copy2(face_path, dest_path)
		except Exception:
			return False
		
		# Add face entry
		face_entry: FaceEntry = {
			'path': str(dest_path.relative_to(self.repository_path)),
			'embedding': embedding,
			'quality_score': quality_score,
			'added_date': datetime.now().isoformat()
		}
		
		data['persons'][person_name]['faces'].append(face_entry)
		data['persons'][person_name]['updated_date'] = datetime.now().isoformat()
		
		return self.save(data)
	
	def list_persons(self) -> List[str]:
		"""List all persons in the repository.
		
		Returns:
			List of person names
		"""
		data = self.load()
		if data is None:
			return []
		return list(data['persons'].keys())
	
	def get_person(self, person_name: str) -> Optional[PersonEntry]:
		"""Get a person's data.
		
		Args:
			person_name: Name of the person
			
		Returns:
			Person entry or None if not found
		"""
		data = self.load()
		if data is None:
			return None
		return data['persons'].get(person_name)
	
	def get_person_face_paths(self, person_name: str) -> List[str]:
		"""Get all face image paths for a person.
		
		Args:
			person_name: Name of the person
			
		Returns:
			List of absolute face image paths
		"""
		person = self.get_person(person_name)
		if person is None:
			return []
		
		paths = []
		for face in person['faces']:
			face_path = self.repository_path / face['path']
			if face_path.exists():
				paths.append(str(face_path.absolute()))
		
		return paths
