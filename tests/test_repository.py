"""Tests for repository system"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from facefusion_repository.cli.repository_cli import RepositoryCLI
from facefusion_repository.core.person_manager import PersonManager
from facefusion_repository.storage.json_storage import JsonStorage


@pytest.fixture
def temp_repo_path():
	"""Create temporary repository path"""
	with tempfile.TemporaryDirectory() as tmpdir:
		yield tmpdir


@pytest.fixture
def temp_test_image(temp_repo_path):
	"""Create a temporary test image"""
	test_image_path = os.path.join(temp_repo_path, 'test_image.jpg')
	# Create a minimal dummy image file
	with open(test_image_path, 'w') as f:
		f.write('dummy image')
	return test_image_path


def test_repository_init(temp_repo_path):
	"""Test repository initialization"""
	storage = JsonStorage(temp_repo_path)
	assert storage.init_repository() is True
	assert storage.repository_exists() is True
	assert os.path.exists(os.path.join(temp_repo_path, 'repository.json'))
	assert os.path.exists(os.path.join(temp_repo_path, 'faces'))


def test_person_manager_add_person(temp_repo_path):
	"""Test adding person to repository"""
	manager = PersonManager(temp_repo_path)
	manager.init_repository()
	
	result = manager.add_person('John Doe')
	assert result['success'] is True
	assert 'person_id' in result['data']
	
	# Try adding same person again
	result2 = manager.add_person('John Doe')
	# This should still succeed but with a different ID due to UUID
	assert result2['success'] is True


def test_person_manager_list_persons(temp_repo_path):
	"""Test listing persons"""
	manager = PersonManager(temp_repo_path)
	manager.init_repository()
	
	# Initially empty
	persons = manager.list_persons()
	assert len(persons) == 0
	
	# Add persons
	manager.add_person('Alice')
	manager.add_person('Bob')
	
	persons = manager.list_persons()
	assert len(persons) == 2


def test_cli_init(temp_repo_path):
	"""Test CLI init command"""
	cli = RepositoryCLI(temp_repo_path)
	result = cli.init_repository()
	
	assert result['success'] is True
	assert 'initialized' in result['message'].lower()


def test_cli_add_face(temp_repo_path, temp_test_image):
	"""Test CLI add face command"""
	cli = RepositoryCLI(temp_repo_path)
	cli.init_repository()
	
	result = cli.add_face(temp_test_image, 'Test Person')
	assert result['success'] is True


def test_cli_list_persons(temp_repo_path, temp_test_image):
	"""Test CLI list persons command"""
	cli = RepositoryCLI(temp_repo_path)
	cli.init_repository()
	
	# Add some faces
	cli.add_face(temp_test_image, 'Person A')
	cli.add_face(temp_test_image, 'Person B')
	
	result = cli.list_persons()
	assert result['success'] is True
	assert 'data' in result
	assert len(result['data']['persons']) == 2


def test_repository_not_initialized(temp_repo_path):
	"""Test operations without initialization"""
	cli = RepositoryCLI(temp_repo_path)
	
	result = cli.add_face('dummy.jpg', 'Test')
	assert result['success'] is False
	assert 'not initialized' in result['message'].lower()


def test_json_storage_database_structure(temp_repo_path):
	"""Test database JSON structure"""
	storage = JsonStorage(temp_repo_path)
	storage.init_repository()
	storage.add_person('test_person', 'Test Person')
	
	db = storage.load_database()
	assert db is not None
	assert 'version' in db
	assert 'persons' in db
	assert len(db['persons']) == 1
	assert db['persons'][0]['person_name'] == 'Test Person'
