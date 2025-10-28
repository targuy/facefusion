"""
Tests for the face repository system.
"""

import os
import tempfile
from pathlib import Path

from facefusion_repository.manager import RepositoryManager


def test_repository_init() -> None:
	"""Test repository initialization."""
	with tempfile.TemporaryDirectory() as temp_dir:
		repo_path = os.path.join(temp_dir, 'test_repo')
		manager = RepositoryManager(repo_path)
		
		# Test initialization
		assert manager.initialize() is True
		assert manager.exists() is True
		
		# Test loading
		data = manager.load()
		assert data is not None
		assert data['version'] == '1.0.0'
		assert data['persons'] == {}


def test_add_person() -> None:
	"""Test adding a person to the repository."""
	with tempfile.TemporaryDirectory() as temp_dir:
		repo_path = os.path.join(temp_dir, 'test_repo')
		manager = RepositoryManager(repo_path)
		manager.initialize()
		
		# Test adding a person
		assert manager.add_person('test_person') is True
		
		# Verify person was added
		persons = manager.list_persons()
		assert 'test_person' in persons
		
		# Verify person data
		person = manager.get_person('test_person')
		assert person is not None
		assert person['name'] == 'test_person'
		assert person['faces'] == []
		
		# Test adding duplicate person
		assert manager.add_person('test_person') is False


def test_add_face() -> None:
	"""Test adding a face to the repository."""
	with tempfile.TemporaryDirectory() as temp_dir:
		repo_path = os.path.join(temp_dir, 'test_repo')
		manager = RepositoryManager(repo_path)
		manager.initialize()
		
		# Create a dummy face image file
		face_file = os.path.join(temp_dir, 'test_face.jpg')
		Path(face_file).touch()
		
		# Test adding a face
		embedding = [0.1] * 128  # Dummy embedding
		quality_score = 0.95
		
		assert manager.add_face('test_person', face_file, embedding, quality_score) is True
		
		# Verify face was added
		person = manager.get_person('test_person')
		assert person is not None
		assert len(person['faces']) == 1
		
		face = person['faces'][0]
		assert face['quality_score'] == quality_score
		assert len(face['embedding']) == 128


def test_get_person_face_paths() -> None:
	"""Test getting face paths for a person."""
	with tempfile.TemporaryDirectory() as temp_dir:
		repo_path = os.path.join(temp_dir, 'test_repo')
		manager = RepositoryManager(repo_path)
		manager.initialize()
		
		# Create a dummy face image file
		face_file = os.path.join(temp_dir, 'test_face.jpg')
		Path(face_file).touch()
		
		# Add face
		embedding = [0.1] * 128
		manager.add_face('test_person', face_file, embedding, 0.95)
		
		# Get face paths
		face_paths = manager.get_person_face_paths('test_person')
		assert len(face_paths) == 1
		assert os.path.exists(face_paths[0])


def test_list_persons() -> None:
	"""Test listing persons in the repository."""
	with tempfile.TemporaryDirectory() as temp_dir:
		repo_path = os.path.join(temp_dir, 'test_repo')
		manager = RepositoryManager(repo_path)
		manager.initialize()
		
		# Add multiple persons
		manager.add_person('person1')
		manager.add_person('person2')
		manager.add_person('person3')
		
		# List persons
		persons = manager.list_persons()
		assert len(persons) == 3
		assert 'person1' in persons
		assert 'person2' in persons
		assert 'person3' in persons


def test_nonexistent_repository() -> None:
	"""Test operations on non-existent repository."""
	with tempfile.TemporaryDirectory() as temp_dir:
		repo_path = os.path.join(temp_dir, 'nonexistent_repo')
		manager = RepositoryManager(repo_path)
		
		# Test operations on non-existent repository
		assert manager.exists() is False
		assert manager.load() is None
		assert manager.list_persons() == []
		assert manager.get_person('test') is None
