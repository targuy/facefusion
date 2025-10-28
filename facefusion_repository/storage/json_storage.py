"""JSON-based storage for FaceFusion Repository"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from facefusion_repository.types import PersonFace, RepositoryDatabase, RepositoryEntry


class JsonStorage:
	"""Handles JSON-based persistence for repository data"""
	
	def __init__(self, repository_path : str = '.facefusion_repository'):
		self.repository_path = repository_path
		self.db_file = os.path.join(repository_path, 'repository.json')
		self.faces_dir = os.path.join(repository_path, 'faces')
		
	def init_repository(self) -> bool:
		"""Initialize repository structure"""
		try:
			os.makedirs(self.faces_dir, exist_ok=True)
			
			if not os.path.exists(self.db_file):
				initial_db : RepositoryDatabase =\
				{
					'version': '1.0.0',
					'persons': []
				}
				self._save_database(initial_db)
			return True
		except Exception:
			return False
	
	def repository_exists(self) -> bool:
		"""Check if repository is initialized"""
		return os.path.exists(self.db_file)
	
	def load_database(self) -> Optional[RepositoryDatabase]:
		"""Load repository database"""
		try:
			if not os.path.exists(self.db_file):
				return None
			with open(self.db_file, 'r') as f:
				return json.load(f)
		except Exception:
			return None
	
	def _save_database(self, database : RepositoryDatabase) -> bool:
		"""Save repository database"""
		try:
			with open(self.db_file, 'w') as f:
				json.dump(database, f, indent=2, default=str)
			return True
		except Exception:
			return False
	
	def add_person(self, person_id : str, person_name : str) -> bool:
		"""Add a new person to repository"""
		database = self.load_database()
		if not database:
			return False
		
		# Check if person already exists
		for person in database['persons']:
			if person['person_id'] == person_id:
				return False
		
		now = datetime.now().isoformat()
		new_person : RepositoryEntry =\
		{
			'person_id': person_id,
			'person_name': person_name,
			'faces': [],
			'created_date': now,
			'modified_date': now
		}
		database['persons'].append(new_person)
		return self._save_database(database)
	
	def get_person(self, person_id : str) -> Optional[RepositoryEntry]:
		"""Get person entry by ID"""
		database = self.load_database()
		if not database:
			return None
		
		for person in database['persons']:
			if person['person_id'] == person_id:
				return person
		return None
	
	def list_persons(self) -> List[RepositoryEntry]:
		"""List all persons in repository"""
		database = self.load_database()
		if not database:
			return []
		return database['persons']
	
	def add_face_to_person(self, person_id : str, face_data : PersonFace) -> bool:
		"""Add a face to a person's entry"""
		database = self.load_database()
		if not database:
			return False
		
		for person in database['persons']:
			if person['person_id'] == person_id:
				person['faces'].append(face_data)
				person['modified_date'] = datetime.now().isoformat()
				return self._save_database(database)
		return False
	
	def get_faces_for_person(self, person_id : str) -> List[PersonFace]:
		"""Get all faces for a person"""
		person = self.get_person(person_id)
		if not person:
			return []
		return person['faces']
	
	def remove_person(self, person_id : str) -> bool:
		"""Remove a person from repository"""
		database = self.load_database()
		if not database:
			return False
		
		database['persons'] = [p for p in database['persons'] if p['person_id'] != person_id]
		return self._save_database(database)
	
	def get_face_directory(self, person_id : str) -> str:
		"""Get directory path for person's faces"""
		person_dir = os.path.join(self.faces_dir, person_id)
		os.makedirs(person_dir, exist_ok=True)
		return person_dir
