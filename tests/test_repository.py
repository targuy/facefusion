"""Tests for the repository system."""

import os
import tempfile
from pathlib import Path

import pytest

from facefusion_repository.manager import RepositoryManager
from facefusion_repository.selector import RepositorySelector
from facefusion_repository.storage import Storage


@pytest.fixture
def temp_repository_path():
	"""Create a temporary repository path."""
	with tempfile.TemporaryDirectory() as temp_dir:
		yield temp_dir


@pytest.fixture
def sample_face_image(temp_repository_path):
	"""Create a sample face image file."""
	image_path = Path(temp_repository_path) / 'test_face.jpg'
	# Create a dummy image file
	image_path.write_bytes(b'dummy image data')
	return str(image_path)


def test_storage_initialization(temp_repository_path):
	"""Test storage initialization."""
	storage = Storage(temp_repository_path)
	assert storage.repository_path.exists()
	assert storage.faces_dir.exists()
	assert storage.data_file.exists()


def test_manager_create_person(temp_repository_path, sample_face_image):
	"""Test creating a person."""
	manager = RepositoryManager(temp_repository_path)
	person = manager.create_person('test_person', [sample_face_image])
	
	assert person['display_name'] == 'test_person'
	assert person['face_count'] == 1
	assert len(person['face_paths']) == 1


def test_manager_list_persons(temp_repository_path, sample_face_image):
	"""Test listing persons."""
	manager = RepositoryManager(temp_repository_path)
	manager.create_person('person1', [sample_face_image])
	manager.create_person('person2', [sample_face_image])
	
	persons = manager.list_persons()
	assert len(persons) == 2
	person_names = [p['display_name'] for p in persons]
	assert 'person1' in person_names
	assert 'person2' in person_names


def test_manager_get_person_by_name(temp_repository_path, sample_face_image):
	"""Test getting a person by name."""
	manager = RepositoryManager(temp_repository_path)
	created_person = manager.create_person('test_person', [sample_face_image])
	
	person = manager.get_person_by_name('test_person')
	assert person is not None
	assert person['display_name'] == 'test_person'
	assert person['person_id'] == created_person['person_id']


def test_manager_remove_person(temp_repository_path, sample_face_image):
	"""Test removing a person."""
	manager = RepositoryManager(temp_repository_path)
	person = manager.create_person('test_person', [sample_face_image])
	
	result = manager.remove_person(person['person_id'])
	assert result is True
	
	persons = manager.list_persons()
	assert len(persons) == 0


def test_selector_get_person_faces(temp_repository_path, sample_face_image):
	"""Test getting faces for a person."""
	manager = RepositoryManager(temp_repository_path)
	manager.create_person('test_person', [sample_face_image])
	
	selector = RepositorySelector(manager)
	face_paths = selector.get_person_faces('test_person')
	
	assert len(face_paths) == 1


def test_selector_fallback_persons(temp_repository_path, sample_face_image):
	"""Test fallback person selection."""
	manager = RepositoryManager(temp_repository_path)
	manager.create_person('fallback_person', [sample_face_image])
	
	selector = RepositorySelector(manager)
	# Try to select non-existent person with fallback
	face_paths = selector.select_faces_for_person('nonexistent', ['fallback_person'])
	
	assert len(face_paths) == 1
