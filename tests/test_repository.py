"""Tests for repository system."""

import os
import tempfile

import pytest

from facefusion_repository import storage, manager, selector
from facefusion.types import Face


@pytest.fixture
def temp_repo_path(monkeypatch):
	"""Create a temporary repository path for testing."""
	temp_dir = tempfile.mkdtemp()
	test_repo = os.path.join(temp_dir, '.facefusion_repository')
	
	# Mock the get_repository_path function to use temp directory
	monkeypatch.setattr(storage, 'get_repository_path', lambda: test_repo)
	
	yield test_repo
	
	# Cleanup
	import shutil
	if os.path.exists(temp_dir):
		shutil.rmtree(temp_dir)


def test_init_repository(temp_repo_path):
	"""Test repository initialization."""
	assert manager.init_repository()
	assert os.path.exists(temp_repo_path)
	assert os.path.exists(os.path.join(temp_repo_path, 'persons'))


def test_person_operations(temp_repo_path):
	"""Test person creation and listing."""
	manager.init_repository()
	
	# Initially empty
	persons = manager.list_repository_persons()
	assert persons == []
	
	# Create a person
	assert storage.create_person('test_person')
	assert storage.person_exists('test_person')
	
	# List persons
	persons = manager.list_repository_persons()
	assert 'test_person' in persons
	
	# Get person info
	info = manager.get_person_info('test_person')
	assert info is not None
	assert info['name'] == 'test_person'
	assert info['face_count'] == 0


def test_calculate_face_pose():
	"""Test face pose calculation."""
	import numpy as np
	
	# Create a mock face with landmarks
	landmarks_5 = np.array([
		[100, 100],  # left eye
		[200, 100],  # right eye
		[150, 150],  # nose
		[120, 200],  # left mouth
		[180, 200]   # right mouth
	])
	
	mock_face = Face(
		bounding_box=np.array([80, 80, 220, 220]),
		score_set={'detector': 0.9},
		landmark_set={'5/68': landmarks_5},
		angle=0,
		embedding=np.random.randn(512),
		embedding_norm=np.random.randn(512),
		gender='male',
		age=range(25, 35),
		race='white'
	)
	
	pitch, yaw, roll = selector.calculate_face_pose(mock_face)
	
	# Basic sanity checks
	assert isinstance(pitch, float)
	assert isinstance(yaw, float)
	assert isinstance(roll, float)
	
	# Roll should be close to 0 for horizontally aligned eyes
	assert abs(roll) < 10


def test_calculate_pose_similarity():
	"""Test pose similarity calculation."""
	pose1 = (0.0, 0.0, 0.0)
	pose2 = (0.0, 0.0, 0.0)
	
	# Identical poses should have similarity 1.0
	similarity = selector.calculate_pose_similarity(pose1, pose2)
	assert similarity == 1.0
	
	# Different poses should have lower similarity
	pose3 = (45.0, 45.0, 0.0)
	similarity = selector.calculate_pose_similarity(pose1, pose3)
	assert 0.0 <= similarity < 1.0


def test_select_optimal_face():
	"""Test optimal face selection."""
	import numpy as np
	
	# Create mock faces with different poses
	def create_mock_face(yaw_offset=0.0):
		landmarks_5 = np.array([
			[100 + yaw_offset, 100],
			[200 + yaw_offset, 100],
			[150 + yaw_offset, 150],
			[120 + yaw_offset, 200],
			[180 + yaw_offset, 200]
		])
		
		return Face(
			bounding_box=np.array([80, 80, 220, 220]),
			score_set={'detector': 0.9},
			landmark_set={'5/68': landmarks_5},
			angle=0,
			embedding=np.random.randn(512),
			embedding_norm=np.random.randn(512),
			gender='male',
			age=range(25, 35),
			race='white'
		)
	
	target_face = create_mock_face(0)
	repo_faces = [
		create_mock_face(0),    # Similar pose
		create_mock_face(30),   # Different pose
		create_mock_face(60)    # Very different pose
	]
	
	optimal_face = selector.select_optimal_face(target_face, repo_faces, min_similarity=0.0)
	
	# Should return a face
	assert optimal_face is not None
	assert optimal_face in repo_faces
