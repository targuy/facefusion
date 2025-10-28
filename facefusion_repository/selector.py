"""Optimal face selector based on 3D pose similarity."""

import math
from typing import List, Optional, Tuple

import numpy

from facefusion.types import Face


def calculate_face_pose(face: Face) -> Tuple[float, float, float]:
	"""Calculate 3D pose (pitch, yaw, roll) from face landmarks.
	
	Args:
		face: Face object with landmarks
		
	Returns:
		Tuple of (pitch, yaw, roll) in degrees
	"""
	# Get 5-point landmarks (eyes, nose, mouth corners)
	landmarks = face.landmark_set.get('5/68')
	if landmarks is None or len(landmarks) < 5:
		return (0.0, 0.0, 0.0)
	
	# landmarks: [left_eye, right_eye, nose, left_mouth, right_mouth]
	left_eye = landmarks[0]
	right_eye = landmarks[1]
	nose = landmarks[2]
	left_mouth = landmarks[3]
	right_mouth = landmarks[4]
	
	# Calculate yaw (left-right rotation) based on eye positions
	eye_center = (left_eye + right_eye) / 2
	nose_to_eye_center = nose - eye_center
	
	# Estimate yaw from horizontal nose offset
	eye_distance = numpy.linalg.norm(right_eye - left_eye)
	if eye_distance > 0:
		yaw = math.degrees(math.atan2(nose_to_eye_center[0], eye_distance))
	else:
		yaw = 0.0
	
	# Calculate pitch (up-down rotation) based on nose and mouth positions
	mouth_center = (left_mouth + right_mouth) / 2
	vertical_distance = mouth_center[1] - nose[1]
	
	if eye_distance > 0:
		pitch = math.degrees(math.atan2(vertical_distance, eye_distance)) - 90
	else:
		pitch = 0.0
	
	# Calculate roll (head tilt) from eye line
	eye_diff = right_eye - left_eye
	roll = math.degrees(math.atan2(eye_diff[1], eye_diff[0]))
	
	return (pitch, yaw, roll)


def calculate_pose_similarity(pose1: Tuple[float, float, float], 
                              pose2: Tuple[float, float, float]) -> float:
	"""Calculate similarity score between two poses.
	
	Args:
		pose1: First pose (pitch, yaw, roll)
		pose2: Second pose (pitch, yaw, roll)
		
	Returns:
		Similarity score (0.0 = very different, 1.0 = identical)
	"""
	pitch1, yaw1, roll1 = pose1
	pitch2, yaw2, roll2 = pose2
	
	# Calculate angular differences
	pitch_diff = abs(pitch1 - pitch2)
	yaw_diff = abs(yaw1 - yaw2)
	roll_diff = abs(roll1 - roll2)
	
	# Normalize differences to [0, 1] range
	# Using 90 degrees as max expected difference
	pitch_sim = 1.0 - min(pitch_diff / 90.0, 1.0)
	yaw_sim = 1.0 - min(yaw_diff / 90.0, 1.0)
	roll_sim = 1.0 - min(roll_diff / 90.0, 1.0)
	
	# Weighted average (yaw is most important for face swapping)
	similarity = (pitch_sim * 0.3 + yaw_sim * 0.5 + roll_sim * 0.2)
	
	return similarity


def select_optimal_face(target_face: Face, 
                       repository_faces: List[Face],
                       min_similarity: float = 0.5) -> Optional[Face]:
	"""Select the optimal repository face based on pose similarity.
	
	Args:
		target_face: The target face to match
		repository_faces: List of available faces from repository
		min_similarity: Minimum similarity threshold (0.0 to 1.0)
		
	Returns:
		Best matching Face or None if no good match found
	"""
	if not repository_faces:
		return None
	
	# Calculate target pose
	target_pose = calculate_face_pose(target_face)
	
	# Calculate similarity for each repository face
	best_face = None
	best_similarity = 0.0
	
	for repo_face in repository_faces:
		repo_pose = calculate_face_pose(repo_face)
		similarity = calculate_pose_similarity(target_pose, repo_pose)
		
		# Also consider face quality (detector score)
		quality_score = repo_face.score_set.get('detector', 0.5)
		
		# Combined score (80% pose similarity, 20% quality)
		combined_score = similarity * 0.8 + quality_score * 0.2
		
		if combined_score > best_similarity:
			best_similarity = combined_score
			best_face = repo_face
	
	# Return best face only if it meets minimum similarity threshold
	if best_similarity >= min_similarity:
		return best_face
	
	# Fallback: return highest quality face
	return max(repository_faces, key=lambda f: f.score_set.get('detector', 0.0))
