"""Pose calculation module for 3D face orientation."""

from typing import Optional, Tuple

import cv2
import numpy


def calculate_3d_pose_from_landmarks(face_landmark_68: numpy.ndarray) -> Tuple[float, float, float]:
	"""
	Calculate 3D pose (pitch, yaw, roll) from 68-point facial landmarks using PnP algorithm.
	
	Args:
		face_landmark_68: 68-point facial landmarks as numpy array of shape (68, 2)
	
	Returns:
		Tuple of (pitch, yaw, roll) in degrees
	"""
	if face_landmark_68 is None or len(face_landmark_68) != 68:
		return (0.0, 0.0, 0.0)
	
	# 3D model points (generic face model in mm)
	model_points = numpy.array([
		(0.0, 0.0, 0.0),             # Nose tip (point 30)
		(0.0, -330.0, -65.0),        # Chin (point 8)
		(-225.0, 170.0, -135.0),     # Left eye left corner (point 36)
		(225.0, 170.0, -135.0),      # Right eye right corner (point 45)
		(-150.0, -150.0, -125.0),    # Left mouth corner (point 48)
		(150.0, -150.0, -125.0)      # Right mouth corner (point 54)
	], dtype=numpy.float64)
	
	# 2D image points from 68-point landmarks
	# Indices: 30 (nose tip), 8 (chin), 36 (left eye left), 45 (right eye right),
	# 48 (left mouth corner), 54 (right mouth corner)
	image_points = numpy.array([
		face_landmark_68[30],  # Nose tip
		face_landmark_68[8],   # Chin
		face_landmark_68[36],  # Left eye left corner
		face_landmark_68[45],  # Right eye right corner
		face_landmark_68[48],  # Left mouth corner
		face_landmark_68[54]   # Right mouth corner
	], dtype=numpy.float64)
	
	# Camera internals (assuming generic camera)
	size = (640, 480)
	focal_length = size[1]
	center = (size[1] / 2, size[0] / 2)
	camera_matrix = numpy.array([
		[focal_length, 0, center[0]],
		[0, focal_length, center[1]],
		[0, 0, 1]
	], dtype=numpy.float64)
	
	# Assume no lens distortion
	dist_coeffs = numpy.zeros((4, 1))
	
	# Solve PnP
	success, rotation_vector, translation_vector = cv2.solvePnP(
		model_points,
		image_points,
		camera_matrix,
		dist_coeffs,
		flags=cv2.SOLVEPNP_ITERATIVE
	)
	
	if not success:
		return (0.0, 0.0, 0.0)
	
	# Convert rotation vector to rotation matrix
	rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
	
	# Extract Euler angles from rotation matrix
	pitch, yaw, roll = rotation_matrix_to_euler_angles(rotation_matrix)
	
	return (pitch, yaw, roll)


def rotation_matrix_to_euler_angles(R: numpy.ndarray) -> Tuple[float, float, float]:
	"""
	Convert rotation matrix to Euler angles (pitch, yaw, roll).
	
	Args:
		R: 3x3 rotation matrix
	
	Returns:
		Tuple of (pitch, yaw, roll) in degrees
	"""
	sy = numpy.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
	
	singular = sy < 1e-6
	
	if not singular:
		pitch = numpy.arctan2(R[2, 1], R[2, 2])
		yaw = numpy.arctan2(-R[2, 0], sy)
		roll = numpy.arctan2(R[1, 0], R[0, 0])
	else:
		pitch = numpy.arctan2(-R[1, 2], R[1, 1])
		yaw = numpy.arctan2(-R[2, 0], sy)
		roll = 0
	
	# Convert to degrees
	pitch = numpy.degrees(pitch)
	yaw = numpy.degrees(yaw)
	roll = numpy.degrees(roll)
	
	return (float(pitch), float(yaw), float(roll))


def calculate_pose_similarity(
	pose1: Tuple[float, float, float],
	pose2: Tuple[float, float, float]
) -> float:
	"""
	Calculate similarity between two poses based on angular distance.
	
	Args:
		pose1: First pose as (pitch, yaw, roll) in degrees
		pose2: Second pose as (pitch, yaw, roll) in degrees
	
	Returns:
		Similarity score from 0.0 (different) to 1.0 (identical)
	"""
	pitch1, yaw1, roll1 = pose1
	pitch2, yaw2, roll2 = pose2
	
	# Calculate angular differences
	pitch_diff = abs(pitch1 - pitch2)
	yaw_diff = abs(yaw1 - yaw2)
	roll_diff = abs(roll1 - roll2)
	
	# Normalize differences to 0-180 range (handle angle wrapping)
	pitch_diff = min(pitch_diff, 360 - pitch_diff)
	yaw_diff = min(yaw_diff, 360 - yaw_diff)
	roll_diff = min(roll_diff, 360 - roll_diff)
	
	# Calculate average angular difference
	avg_diff = (pitch_diff + yaw_diff + roll_diff) / 3.0
	
	# Convert to similarity score (0 degrees = 1.0, 90 degrees = 0.0)
	similarity = max(0.0, 1.0 - (avg_diff / 90.0))
	
	return float(similarity)


def is_pose_within_tolerance(
	pose1: Tuple[float, float, float],
	pose2: Tuple[float, float, float],
	tolerance: float = 15.0
) -> bool:
	"""
	Check if two poses are within the specified angular tolerance.
	
	Args:
		pose1: First pose as (pitch, yaw, roll) in degrees
		pose2: Second pose as (pitch, yaw, roll) in degrees
		tolerance: Maximum angular difference in degrees (default: 15.0)
	
	Returns:
		True if poses are within tolerance, False otherwise
	"""
	pitch1, yaw1, roll1 = pose1
	pitch2, yaw2, roll2 = pose2
	
	# Calculate angular differences
	pitch_diff = abs(pitch1 - pitch2)
	yaw_diff = abs(yaw1 - yaw2)
	roll_diff = abs(roll1 - roll2)
	
	# Normalize differences to 0-180 range (handle angle wrapping)
	pitch_diff = min(pitch_diff, 360 - pitch_diff)
	yaw_diff = min(yaw_diff, 360 - yaw_diff)
	roll_diff = min(roll_diff, 360 - roll_diff)
	
	# Check if all angles are within tolerance
	return pitch_diff <= tolerance and yaw_diff <= tolerance and roll_diff <= tolerance
