"""Tests for orientation-based face selection."""

import numpy
import pytest

from facefusion_repository.orientation import (
	calculate_orientation_distance,
	check_orientation_overlap,
	extract_3d_orientation_from_landmarks,
	select_best_repo_face_by_orientation
)


class TestOrientationDistance:
	"""Test orientation distance calculation."""
	
	def test_identical_orientations(self):
		"""Test that identical orientations have zero distance."""
		orientation1 = {'pitch': 10.0, 'yaw': 20.0, 'roll': 5.0}
		orientation2 = {'pitch': 10.0, 'yaw': 20.0, 'roll': 5.0}
		
		distance = calculate_orientation_distance(orientation1, orientation2)
		assert distance == 0.0
	
	def test_different_yaw_only(self):
		"""Test distance calculation with only yaw difference."""
		orientation1 = {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
		orientation2 = {'pitch': 0.0, 'yaw': 10.0, 'roll': 0.0}
		
		distance = calculate_orientation_distance(orientation1, orientation2)
		# Yaw weight is 1.0, so distance should be 10.0
		assert distance == pytest.approx(10.0, rel=0.01)
	
	def test_different_pitch_only(self):
		"""Test distance calculation with only pitch difference."""
		orientation1 = {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
		orientation2 = {'pitch': 10.0, 'yaw': 0.0, 'roll': 0.0}
		
		distance = calculate_orientation_distance(orientation1, orientation2)
		# Pitch weight is 0.7, so distance should be 7.0
		assert distance == pytest.approx(7.0, rel=0.01)
	
	def test_different_roll_only(self):
		"""Test distance calculation with only roll difference."""
		orientation1 = {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
		orientation2 = {'pitch': 0.0, 'yaw': 0.0, 'roll': 10.0}
		
		distance = calculate_orientation_distance(orientation1, orientation2)
		# Roll weight is 0.3, so distance should be 3.0
		assert distance == pytest.approx(3.0, rel=0.01)
	
	def test_yaw_circular_wrapping(self):
		"""Test that yaw wrapping is handled correctly (-180 = +180)."""
		orientation1 = {'pitch': 0.0, 'yaw': -170.0, 'roll': 0.0}
		orientation2 = {'pitch': 0.0, 'yaw': 170.0, 'roll': 0.0}
		
		distance = calculate_orientation_distance(orientation1, orientation2)
		# Angular difference should be 20 degrees (not 340)
		assert distance == pytest.approx(20.0, rel=0.01)
	
	def test_combined_differences(self):
		"""Test weighted euclidean distance with all axes different."""
		orientation1 = {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
		orientation2 = {'pitch': 10.0, 'yaw': 10.0, 'roll': 10.0}
		
		distance = calculate_orientation_distance(orientation1, orientation2)
		# Expected: sqrt((1.0*10)^2 + (0.7*10)^2 + (0.3*10)^2)
		# = sqrt(100 + 49 + 9) = sqrt(158) ≈ 12.57
		expected = numpy.sqrt(100 + 49 + 9)
		assert distance == pytest.approx(expected, rel=0.01)
	
	def test_missing_orientation_keys(self):
		"""Test handling of missing orientation keys (default to 0)."""
		orientation1 = {'pitch': 10.0}
		orientation2 = {'yaw': 20.0}
		
		# Should handle missing keys gracefully (default to 0.0)
		distance = calculate_orientation_distance(orientation1, orientation2)
		# Expected: sqrt((1.0*20)^2 + (0.7*10)^2 + (0.3*0)^2)
		# = sqrt(400 + 49 + 0) = sqrt(449) ≈ 21.19
		expected = numpy.sqrt(400 + 49)
		assert distance == pytest.approx(expected, rel=0.01)


class TestOrientationOverlap:
	"""Test orientation overlap detection."""
	
	def test_no_overlap(self):
		"""Test that non-overlapping orientations are not detected as overlaps."""
		new_orientation = {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
		existing_orientations = [
			{'pitch': 30.0, 'yaw': 30.0, 'roll': 30.0},
			{'pitch': -30.0, 'yaw': -30.0, 'roll': -30.0}
		]
		
		overlap_idx = check_orientation_overlap(new_orientation, existing_orientations, tolerance=15.0)
		assert overlap_idx is None
	
	def test_overlap_detected(self):
		"""Test that overlapping orientations are detected."""
		new_orientation = {'pitch': 10.0, 'yaw': 10.0, 'roll': 10.0}
		existing_orientations = [
			{'pitch': 5.0, 'yaw': 5.0, 'roll': 5.0},  # Within 15 degree tolerance
			{'pitch': 50.0, 'yaw': 50.0, 'roll': 50.0}
		]
		
		overlap_idx = check_orientation_overlap(new_orientation, existing_orientations, tolerance=15.0)
		assert overlap_idx == 0  # Should match first orientation
	
	def test_overlap_exact_tolerance(self):
		"""Test overlap detection at exact tolerance boundary."""
		new_orientation = {'pitch': 15.0, 'yaw': 15.0, 'roll': 15.0}
		existing_orientations = [
			{'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
		]
		
		overlap_idx = check_orientation_overlap(new_orientation, existing_orientations, tolerance=15.0)
		assert overlap_idx == 0  # Should match (exactly at boundary)
	
	def test_overlap_just_outside_tolerance(self):
		"""Test that orientations just outside tolerance are not detected."""
		new_orientation = {'pitch': 16.0, 'yaw': 16.0, 'roll': 16.0}
		existing_orientations = [
			{'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
		]
		
		overlap_idx = check_orientation_overlap(new_orientation, existing_orientations, tolerance=15.0)
		assert overlap_idx is None  # Should NOT match (outside tolerance)
	
	def test_overlap_with_yaw_wrapping(self):
		"""Test overlap detection with yaw circular wrapping."""
		new_orientation = {'pitch': 0.0, 'yaw': 175.0, 'roll': 0.0}
		existing_orientations = [
			{'pitch': 0.0, 'yaw': -175.0, 'roll': 0.0}  # 10 degrees apart with wrapping
		]
		
		overlap_idx = check_orientation_overlap(new_orientation, existing_orientations, tolerance=15.0)
		assert overlap_idx == 0  # Should match (10 < 15)
	
	def test_overlap_empty_list(self):
		"""Test overlap detection with no existing orientations."""
		new_orientation = {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
		existing_orientations = []
		
		overlap_idx = check_orientation_overlap(new_orientation, existing_orientations, tolerance=15.0)
		assert overlap_idx is None


class TestBestFaceSelection:
	"""Test best face selection by orientation."""
	
	def test_select_closest_face(self):
		"""Test that the closest matching face is selected."""
		target_orientation = {'pitch': 10.0, 'yaw': 10.0, 'roll': 10.0}
		person_repo_faces = [
			{'path': '/path/face1.jpg', 'orientation': {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}},
			{'path': '/path/face2.jpg', 'orientation': {'pitch': 11.0, 'yaw': 11.0, 'roll': 11.0}},  # Closest
			{'path': '/path/face3.jpg', 'orientation': {'pitch': 30.0, 'yaw': 30.0, 'roll': 30.0}}
		]
		
		best_face = select_best_repo_face_by_orientation(target_orientation, person_repo_faces)
		assert best_face['path'] == '/path/face2.jpg'
	
	def test_select_from_empty_list(self):
		"""Test selection from empty face list."""
		target_orientation = {'pitch': 10.0, 'yaw': 10.0, 'roll': 10.0}
		person_repo_faces = []
		
		best_face = select_best_repo_face_by_orientation(target_orientation, person_repo_faces)
		assert best_face is None
	
	def test_select_face_without_orientation(self):
		"""Test that faces without orientation fall back to first face."""
		target_orientation = {'pitch': 10.0, 'yaw': 10.0, 'roll': 10.0}
		person_repo_faces = [
			{'path': '/path/face1.jpg'},  # No orientation
			{'path': '/path/face2.jpg'}   # No orientation
		]
		
		best_face = select_best_repo_face_by_orientation(target_orientation, person_repo_faces)
		assert best_face['path'] == '/path/face1.jpg'  # Falls back to first
	
	def test_select_with_partial_orientations(self):
		"""Test selection when some faces have orientation and some don't."""
		target_orientation = {'pitch': 10.0, 'yaw': 10.0, 'roll': 10.0}
		person_repo_faces = [
			{'path': '/path/face1.jpg'},  # No orientation
			{'path': '/path/face2.jpg', 'orientation': {'pitch': 9.0, 'yaw': 9.0, 'roll': 9.0}},  # Closest
			{'path': '/path/face3.jpg', 'orientation': {'pitch': 50.0, 'yaw': 50.0, 'roll': 50.0}}
		]
		
		best_face = select_best_repo_face_by_orientation(target_orientation, person_repo_faces)
		assert best_face['path'] == '/path/face2.jpg'
	
	def test_select_with_yaw_wrapping(self):
		"""Test selection with yaw circular wrapping."""
		target_orientation = {'pitch': 0.0, 'yaw': -170.0, 'roll': 0.0}
		person_repo_faces = [
			{'path': '/path/face1.jpg', 'orientation': {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}},
			{'path': '/path/face2.jpg', 'orientation': {'pitch': 0.0, 'yaw': 170.0, 'roll': 0.0}}  # Closest (20° apart)
		]
		
		best_face = select_best_repo_face_by_orientation(target_orientation, person_repo_faces)
		assert best_face['path'] == '/path/face2.jpg'


class TestLandmarkOrientationExtraction:
	"""Test orientation extraction from landmarks."""
	
	def test_extract_from_valid_landmarks(self):
		"""Test extraction from valid 68-point landmarks."""
		# Create dummy 68-point landmarks (neutral face orientation)
		landmarks = numpy.array([
			[i * 5, i * 5] for i in range(68)
		], dtype=numpy.float64)
		
		orientation = extract_3d_orientation_from_landmarks(landmarks)
		
		# Should return a dict with pitch, yaw, roll
		assert 'pitch' in orientation
		assert 'yaw' in orientation
		assert 'roll' in orientation
		assert isinstance(orientation['pitch'], float)
		assert isinstance(orientation['yaw'], float)
		assert isinstance(orientation['roll'], float)
	
	def test_extract_from_insufficient_landmarks(self):
		"""Test extraction with insufficient landmarks."""
		# Only 10 landmarks instead of 68
		landmarks = numpy.array([
			[i * 5, i * 5] for i in range(10)
		], dtype=numpy.float64)
		
		orientation = extract_3d_orientation_from_landmarks(landmarks)
		
		# Should return neutral orientation (0, 0, 0)
		assert orientation == {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
	
	def test_extract_from_none(self):
		"""Test extraction from None landmarks."""
		orientation = extract_3d_orientation_from_landmarks(None)
		
		# Should return neutral orientation (0, 0, 0)
		assert orientation == {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
