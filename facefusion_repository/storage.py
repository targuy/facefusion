"""Storage layer for repository system."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.types import PersonEntry, RepositoryStorage


DEFAULT_REPOSITORY_PATH = '.face_repository'


class Storage:
	"""Handles persistent storage of face repository data."""

	def __init__(self, repository_path: str = DEFAULT_REPOSITORY_PATH):
		self.repository_path = Path(repository_path)
		self.data_file = self.repository_path / 'repository.json'
		self.faces_dir = self.repository_path / 'faces'
		self._ensure_structure()

	def _ensure_structure(self) -> None:
		"""Ensure repository directory structure exists."""
		self.repository_path.mkdir(parents=True, exist_ok=True)
		self.faces_dir.mkdir(parents=True, exist_ok=True)
		if not self.data_file.exists():
			self._save_data({'version': '1.0.0', 'persons': {}})

	def _load_data(self) -> RepositoryStorage:
		"""Load repository data from disk."""
		with open(self.data_file, 'r') as f:
			return json.load(f)

	def _save_data(self, data: RepositoryStorage) -> None:
		"""Save repository data to disk."""
		with open(self.data_file, 'w') as f:
			json.dump(data, f, indent=2)

	def get_all_persons(self) -> Dict[str, PersonEntry]:
		"""Get all persons from repository."""
		data = self._load_data()
		return data.get('persons', {})

	def get_person(self, person_id: str) -> Optional[PersonEntry]:
		"""Get a specific person by ID."""
		persons = self.get_all_persons()
		return persons.get(person_id)

	def add_person(self, person: PersonEntry) -> None:
		"""Add a person to the repository."""
		data = self._load_data()
		data['persons'][person['person_id']] = person
		self._save_data(data)

	def remove_person(self, person_id: str) -> bool:
		"""Remove a person from the repository."""
		data = self._load_data()
		if person_id in data['persons']:
			del data['persons'][person_id]
			self._save_data(data)
			return True
		return False

	def update_person(self, person_id: str, updates: Dict) -> bool:
		"""Update a person's data."""
		data = self._load_data()
		if person_id in data['persons']:
			data['persons'][person_id].update(updates)
			self._save_data(data)
			return True
		return False

	def get_person_face_dir(self, person_id: str) -> Path:
		"""Get the directory for a person's faces."""
		person_dir = self.faces_dir / person_id
		person_dir.mkdir(parents=True, exist_ok=True)
		return person_dir
