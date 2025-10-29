"""Integration tests for orientation-based repository workflow."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy
import pytest

from facefusion_repository.manager import RepositoryManager
from facefusion_repository.selector import RepositorySelector


@pytest.fixture
def mock_face_detector():
	"""Mock face detector to avoid needing real models."""
	with patch('facefusion_repository.orientation.face_detector') as mock:
		# Create a mock face with 68-point landmarks
		mock_face = MagicMock()
		mock_face.landmark_set = {
			'68': numpy.array([[i * 5, i * 5] for i in range(68)], dtype=numpy.float64)
		}
		mock.detect_faces.return_value = [mock_face]
		yield mock


@pytest.fixture
def mock_face_landmarker():
	"""Mock face landmarker."""
	with patch('facefusion_repository.orientation.face_landmarker') as mock:
		yield mock


@pytest.fixture
def mock_read_image():
	"""Mock image reading."""
	with patch('facefusion_repository.orientation.read_static_image') as mock:
		# Return a dummy image array
		mock.return_value = numpy.zeros((512, 512, 3), dtype=numpy.uint8)
		yield mock


@pytest.fixture
def temp_repository_path():
	"""Create a temporary repository path."""
	with tempfile.TemporaryDirectory() as temp_dir:
		yield temp_dir


@pytest.fixture
def sample_face_images(temp_repository_path):
	"""Create sample face image files."""
	image_dir = Path(temp_repository_path) / 'test_images'
	image_dir.mkdir()
	
	face_images = []
	for i in range(3):
		image_path = image_dir / f'face_{i}.jpg'
		# Create a simple dummy image (just write some bytes)
		image_path.write_bytes(b'dummy image data')
		face_images.append(str(image_path))
	
	return face_images


class TestOrientationWorkflow:
	"""Test complete orientation-based workflow."""
	
	def test_create_person_with_orientation_extraction(
		self,
		temp_repository_path,
		sample_face_images,
		mock_face_detector,
		mock_face_landmarker,
		mock_read_image
	):
		"""Test creating a person with orientation extraction enabled."""
		# Mock to return different orientations for each face to avoid overlaps
		with patch('facefusion_repository.orientation.extract_3d_orientation_from_landmarks') as mock_extract:
			# Return different orientations for each call
			orientations = [
				{'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0},
				{'pitch': 30.0, 'yaw': 30.0, 'roll': 30.0},
				{'pitch': 60.0, 'yaw': 60.0, 'roll': 60.0}
			]
			mock_extract.side_effect = orientations
			
			manager = RepositoryManager(temp_repository_path)
			
			# Create person with orientation extraction
			person = manager.create_person(
				'test_person',
				sample_face_images,
				assess_quality=False,
				extract_orientation=True
			)
			
			# Verify person was created
			assert person['display_name'] == 'test_person'
			assert person['face_count'] == 3
			
			# Verify orientation metadata was stored
			face_metadata = person.get('face_metadata')
			assert face_metadata is not None
			
			# Check that at least one face has pose metadata
			has_pose = any('pose' in metadata for metadata in face_metadata.values())
			assert has_pose, "Expected at least one face to have pose metadata"
	
	def test_orientation_overlap_detection(
		self,
		temp_repository_path,
		sample_face_images,
		mock_face_detector,
		mock_face_landmarker,
		mock_read_image
	):
		"""Test that orientation overlaps are detected during import."""
		# Mock to return same orientation for all faces (simulating overlap)
		with patch('facefusion_repository.orientation.extract_3d_orientation_from_landmarks') as mock_extract:
			# All faces will have same orientation
			mock_extract.return_value = {'pitch': 10.0, 'yaw': 20.0, 'roll': 5.0}
			
			manager = RepositoryManager(temp_repository_path)
			
			# Create person with strict tolerance
			person = manager.create_person(
				'test_person',
				sample_face_images,
				assess_quality=False,
				extract_orientation=True,
				orientation_tolerance=5.0  # Very strict
			)
			
			# Due to overlap detection, only one face should be kept
			assert person['face_count'] == 1
	
	def test_select_best_face_by_orientation(
		self,
		temp_repository_path,
		sample_face_images,
		mock_face_detector,
		mock_face_landmarker,
		mock_read_image
	):
		"""Test selecting best face by orientation."""
		# Mock to return different orientations for each face
		orientations = [
			{'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0},
			{'pitch': 10.0, 'yaw': 10.0, 'roll': 10.0},
			{'pitch': 30.0, 'yaw': 30.0, 'roll': 30.0}
		]
		
		with patch('facefusion_repository.orientation.extract_3d_orientation_from_landmarks') as mock_extract:
			# Return different orientations for each call
			mock_extract.side_effect = orientations
			
			manager = RepositoryManager(temp_repository_path)
			
			# Create person with no overlap (tolerance strict, but faces are far apart)
			person = manager.create_person(
				'test_person',
				sample_face_images,
				assess_quality=False,
				extract_orientation=True,
				orientation_tolerance=5.0
			)
			
			# All faces should be kept (different orientations)
			assert person['face_count'] == 3
			
			# Test selection
			selector = RepositorySelector(manager)
			
			# Target orientation closest to second face
			target_orientation = {'pitch': 11.0, 'yaw': 11.0, 'roll': 11.0}
			best_face = selector.get_best_face_by_orientation('test_person', target_orientation)
			
			# Should select a face (exact match depends on stored paths)
			assert best_face is not None
			assert isinstance(best_face, str)
	
	def test_person_specific_selection(
		self,
		temp_repository_path,
		sample_face_images,
		mock_face_detector,
		mock_face_landmarker,
		mock_read_image
	):
		"""Test that face selection is person-specific."""
		with patch('facefusion_repository.orientation.extract_3d_orientation_from_landmarks') as mock_extract:
			mock_extract.return_value = {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
			
			manager = RepositoryManager(temp_repository_path)
			
			# Create two different persons
			person1 = manager.create_person(
				'person1',
				[sample_face_images[0]],
				assess_quality=False,
				extract_orientation=True
			)
			
			person2 = manager.create_person(
				'person2',
				[sample_face_images[1]],
				assess_quality=False,
				extract_orientation=True
			)
			
			# Verify both persons exist
			assert person1['face_count'] == 1
			assert person2['face_count'] == 1
			
			selector = RepositorySelector(manager)
			
			# Get face for person1
			face1 = selector.get_best_face_by_orientation(
				'person1',
				{'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
			)
			
			# Get face for person2
			face2 = selector.get_best_face_by_orientation(
				'person2',
				{'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
			)
			
			# Faces should be different (from different persons)
			assert face1 != face2
	
	def test_quality_comparison_on_orientation_overlap(
		self,
		temp_repository_path,
		sample_face_images,
		mock_face_detector,
		mock_face_landmarker,
		mock_read_image
	):
		"""Test that quality is compared when orientation overlaps are detected."""
		from facefusion_repository.quality_assessor import QualityMetrics
		
		# Expected behavior: when faces have overlapping orientations,
		# the system should keep the highest quality face
		LOW_QUALITY = 0.3
		HIGH_QUALITY = 0.8
		MEDIUM_QUALITY = 0.6
		
		# Mock orientation extraction to return same orientation
		with patch('facefusion_repository.orientation.extract_3d_orientation_from_landmarks') as mock_extract:
			mock_extract.return_value = {'pitch': 10.0, 'yaw': 20.0, 'roll': 5.0}
			
			# Mock quality assessment to return different qualities
			with patch('facefusion_repository.manager.assess_face_from_path') as mock_quality:
				# Provide enough quality assessments for the workflow
				qualities = [
					QualityMetrics(LOW_QUALITY, LOW_QUALITY, LOW_QUALITY, LOW_QUALITY, LOW_QUALITY),
					QualityMetrics(HIGH_QUALITY, HIGH_QUALITY, HIGH_QUALITY, HIGH_QUALITY, HIGH_QUALITY),
					QualityMetrics(HIGH_QUALITY, HIGH_QUALITY, HIGH_QUALITY, HIGH_QUALITY, HIGH_QUALITY),
					QualityMetrics(MEDIUM_QUALITY, MEDIUM_QUALITY, MEDIUM_QUALITY, MEDIUM_QUALITY, MEDIUM_QUALITY)
				]
				mock_quality.side_effect = qualities
				
				manager = RepositoryManager(temp_repository_path)
				
				# Create person with quality assessment and orientation overlap detection
				person = manager.create_person(
					'test_person',
					sample_face_images,
					assess_quality=True,
					extract_orientation=True,
					orientation_tolerance=15.0
				)
				
				# Should keep only the highest quality face
				assert person['face_count'] == 1
				
				# Verify the kept face has the best quality
				face_metadata = person.get('face_metadata')
				for metadata in face_metadata.values():
					if 'quality' in metadata:
						assert metadata['quality']['overall'] == pytest.approx(HIGH_QUALITY, rel=0.01)


class TestBackwardCompatibility:
	"""Test backward compatibility with existing functionality."""
	
	def test_create_person_without_orientation(
		self,
		temp_repository_path,
		sample_face_images
	):
		"""Test that orientation extraction can be disabled."""
		manager = RepositoryManager(temp_repository_path)
		
		# Create person without orientation extraction
		person = manager.create_person(
			'test_person',
			sample_face_images,
			assess_quality=False,
			extract_orientation=False
		)
		
		# Person should be created normally
		assert person['display_name'] == 'test_person'
		assert person['face_count'] == 3
	
	def test_fallback_when_no_orientation_metadata(
		self,
		temp_repository_path,
		sample_face_images
	):
		"""Test that selector falls back gracefully when no orientation metadata."""
		manager = RepositoryManager(temp_repository_path)
		
		# Create person without orientation
		person = manager.create_person(
			'test_person',
			sample_face_images,
			assess_quality=False,
			extract_orientation=False
		)
		
		selector = RepositorySelector(manager)
		
		# Try to select by orientation (should fall back to first face)
		target_orientation = {'pitch': 10.0, 'yaw': 20.0, 'roll': 5.0}
		best_face = selector.get_best_face_by_orientation('test_person', target_orientation)
		
		# Should return first face as fallback
		assert best_face is not None
		assert best_face == person['face_paths'][0]
