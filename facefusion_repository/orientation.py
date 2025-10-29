"""Orientation utilities for face repository system."""

import math
from typing import Dict, List, Optional, Tuple

import cv2
import numpy

from facefusion import face_detector, face_landmarker, logger
from facefusion.types import Face
from facefusion.vision import read_static_image


def calculate_orientation_distance(
	target_orientation: Dict[str, float],
	repo_orientation: Dict[str, float]
) -> float:
	"""
	Calculate weighted Euclidean distance between two 3D orientations.
	
	Uses weighted angular distance with:
	- Yaw weight: 1.0 (most important for face matching)
	- Pitch weight: 0.7 (important but less than yaw)
	- Roll weight: 0.3 (least important)
	
	Handles circular angle wrapping for yaw axis (-180° = +180°).
	
	Args:
		target_orientation: Target face orientation {'pitch': float, 'yaw': float, 'roll': float}
		repo_orientation: Repository face orientation {'pitch': float, 'yaw': float, 'roll': float}
	
	Returns:
		Weighted Euclidean distance between orientations (lower is better match)
	"""
	# Extract angles
	target_pitch = target_orientation.get('pitch', 0.0)
	target_yaw = target_orientation.get('yaw', 0.0)
	target_roll = target_orientation.get('roll', 0.0)
	
	repo_pitch = repo_orientation.get('pitch', 0.0)
	repo_yaw = repo_orientation.get('yaw', 0.0)
	repo_roll = repo_orientation.get('roll', 0.0)
	
	# Calculate angular differences
	pitch_diff = abs(target_pitch - repo_pitch)
	roll_diff = abs(target_roll - repo_roll)
	
	# Handle circular yaw wrapping (-180° = +180°)
	yaw_diff = abs(target_yaw - repo_yaw)
	if yaw_diff > 180.0:
		yaw_diff = 360.0 - yaw_diff
	
	# Apply weights and calculate weighted Euclidean distance
	yaw_weight = 1.0
	pitch_weight = 0.7
	roll_weight = 0.3
	
	weighted_distance = math.sqrt(
		(yaw_weight * yaw_diff) ** 2 +
		(pitch_weight * pitch_diff) ** 2 +
		(roll_weight * roll_diff) ** 2
	)
	
	return weighted_distance


def extract_3d_orientation_from_landmarks(face_landmark_68: numpy.ndarray) -> Dict[str, float]:
	"""
	Extract 3D orientation (pitch, yaw, roll) from 68-point facial landmarks.
	
	Uses the existing pose calculator from the repository.
	
	Args:
		face_landmark_68: 68-point facial landmarks as numpy array of shape (68, 2)
	
	Returns:
		Dictionary with 'pitch', 'yaw', 'roll' angles in degrees
	"""
	from facefusion_repository.pose_calculator import calculate_3d_pose_from_landmarks
	
	pitch, yaw, roll = calculate_3d_pose_from_landmarks(face_landmark_68)
	
	return {
		'pitch': float(pitch),
		'yaw': float(yaw),
		'roll': float(roll)
	}


def extract_3d_orientation(face: Face) -> Dict[str, float]:
	"""
	Extract 3D orientation (pitch, yaw, roll) from Face object.
	
	Args:
		face: Face object with landmark_set containing 68-point landmarks
	
	Returns:
		Dictionary with 'pitch', 'yaw', 'roll' angles in degrees
	"""
	# Get 68-point landmarks from face
	if face.landmark_set is None or '68' not in face.landmark_set:
		# If no 68-point landmarks, return neutral orientation
		return {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
	
	face_landmark_68 = face.landmark_set['68']
	return extract_3d_orientation_from_landmarks(face_landmark_68)


def extract_orientation_from_image_path(image_path: str) -> Optional[Dict[str, float]]:
	"""
	Extract 3D orientation from a face image file.
	
	Detects the face in the image, extracts landmarks, and calculates orientation.
	If multiple faces are detected, uses the largest face.
	
	Args:
		image_path: Path to face image file
	
	Returns:
		Dictionary with 'pitch', 'yaw', 'roll' angles in degrees, or None if no face detected
	"""
	try:
		# Read image
		image = read_static_image(image_path)
		if image is None:
			logger.warn(f"Could not read image: {image_path}", __name__.upper())
			return None
		
		# Detect faces
		faces = face_detector.detect_faces(image)
		if not faces:
			logger.warn(f"No face detected in image: {image_path}", __name__.upper())
			return None
		
		# Use the first (or largest) face
		face = faces[0]
		
		# Ensure we have 68-point landmarks for pose estimation
		if face.landmark_set is None or '68' not in face.landmark_set:
			# Extract 68-point landmarks if not present
			face = face_landmarker.detect_face_landmarks(image, face, '68')
			if face.landmark_set is None or '68' not in face.landmark_set:
				logger.warn(f"Could not extract 68-point landmarks from: {image_path}", __name__.upper())
				return None
		
		# Extract orientation
		return extract_3d_orientation(face)
	
	except Exception as error:
		logger.error(f"Error extracting orientation from {image_path}: {error}", __name__.upper())
		return None


def check_orientation_overlap(
	new_orientation: Dict[str, float],
	existing_orientations: List[Dict[str, float]],
	tolerance: float = 15.0
) -> Optional[int]:
	"""
	Check if new orientation overlaps with any existing orientations.
	
	Used during face import to detect orientation conflicts.
	An overlap is detected when the angular distance between orientations
	is within the tolerance threshold for all three axes.
	
	Args:
		new_orientation: New face orientation to check
		existing_orientations: List of existing face orientations
		tolerance: Maximum angular difference in degrees for overlap detection (default: 15.0)
	
	Returns:
		Index of overlapping orientation if found, None otherwise
	"""
	new_pitch = new_orientation.get('pitch', 0.0)
	new_yaw = new_orientation.get('yaw', 0.0)
	new_roll = new_orientation.get('roll', 0.0)
	
	for idx, existing in enumerate(existing_orientations):
		existing_pitch = existing.get('pitch', 0.0)
		existing_yaw = existing.get('yaw', 0.0)
		existing_roll = existing.get('roll', 0.0)
		
		# Calculate angular differences
		pitch_diff = abs(new_pitch - existing_pitch)
		roll_diff = abs(new_roll - existing_roll)
		
		# Handle circular yaw wrapping
		yaw_diff = abs(new_yaw - existing_yaw)
		if yaw_diff > 180.0:
			yaw_diff = 360.0 - yaw_diff
		
		# Check if all angles are within tolerance
		if pitch_diff <= tolerance and yaw_diff <= tolerance and roll_diff <= tolerance:
			return idx
	
	return None


def select_best_repo_face_by_orientation(
	target_face_orientation: Dict[str, float],
	person_repo_faces: List[Dict[str, any]]
) -> Optional[Dict[str, any]]:
	"""
	Select best repository face based on orientation proximity to target.
	
	Only selects from faces belonging to ONE person. Never compares across persons.
	This is an automatic algorithmic selection without user input.
	
	Args:
		target_face_orientation: Target face orientation to match
		person_repo_faces: List of repository faces from a SINGLE person.
			Each face should have 'orientation' and 'path' keys.
	
	Returns:
		Best matching repository face dict, or None if no faces provided
	"""
	if not person_repo_faces:
		return None
	
	best_face = None
	best_distance = float('inf')
	
	for repo_face in person_repo_faces:
		if 'orientation' not in repo_face:
			# Skip faces without orientation data
			continue
		
		distance = calculate_orientation_distance(
			target_face_orientation,
			repo_face['orientation']
		)
		
		if distance < best_distance:
			best_distance = distance
			best_face = repo_face
	
	# If no face with orientation found, return first face as fallback
	return best_face if best_face is not None else person_repo_faces[0]
