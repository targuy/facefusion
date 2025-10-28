"""3D face pose analysis for repository"""

import math
from typing import Any, Dict, Optional

import numpy
from numpy.typing import NDArray

from facefusion_repository.types import Pose3D


class FaceAnalyzer:
	"""Analyzes face pose and orientation"""
	
	def analyze_pose(self, face_data : Dict[str, Any]) -> Pose3D:
		"""Analyze 3D pose of face from landmarks"""
		landmarks = face_data.get('landmark_set', {}).get('68')
		
		if landmarks is None or len(landmarks) < 68:
			# Return neutral pose if landmarks unavailable
			return\
			{
				'yaw': 0.0,
				'pitch': 0.0,
				'roll': 0.0,
				'confidence': 0.0
			}
		
		yaw, pitch, roll = self._estimate_head_pose(landmarks)
		confidence = self._calculate_pose_confidence(landmarks)
		
		return\
		{
			'yaw': float(yaw),
			'pitch': float(pitch),
			'roll': float(roll),
			'confidence': float(confidence)
		}
	
	def _estimate_head_pose(self, landmarks : NDArray[Any]) -> tuple[float, float, float]:
		"""Estimate head pose angles from facial landmarks"""
		try:
			# Use key landmarks for pose estimation
			# Nose tip (30), left eye (36), right eye (45), left mouth (48), right mouth (54)
			nose_tip = landmarks[30]
			left_eye = landmarks[36]
			right_eye = landmarks[45]
			left_mouth = landmarks[48]
			right_mouth = landmarks[54]
			
			# Calculate yaw (horizontal rotation)
			eye_center = (left_eye + right_eye) / 2
			eye_to_nose = nose_tip - eye_center
			yaw = math.degrees(math.atan2(eye_to_nose[0], abs(eye_to_nose[1]) + 1e-6))
			
			# Calculate pitch (vertical rotation)
			mouth_center = (left_mouth + right_mouth) / 2
			eye_to_mouth = mouth_center - eye_center
			pitch = math.degrees(math.atan2(eye_to_mouth[1], abs(eye_to_mouth[0]) + 1e-6))
			
			# Calculate roll (tilt)
			eye_angle = right_eye - left_eye
			roll = math.degrees(math.atan2(eye_angle[1], eye_angle[0]))
			
			return yaw, pitch, roll
		except Exception:
			return 0.0, 0.0, 0.0
	
	def _calculate_pose_confidence(self, landmarks : NDArray[Any]) -> float:
		"""Calculate confidence in pose estimation"""
		try:
			# Check landmark quality based on distribution
			variance = numpy.var(landmarks, axis=0)
			confidence = min(numpy.sum(variance) / 1000.0, 1.0)
			return confidence
		except Exception:
			return 0.5
	
	def is_frontal_pose(self, pose : Pose3D, tolerance : float = 15.0) -> bool:
		"""Check if pose is frontal (within tolerance degrees)"""
		return (
			abs(pose['yaw']) < tolerance and
			abs(pose['pitch']) < tolerance and
			abs(pose['roll']) < tolerance
		)
	
	def get_pose_category(self, pose : Pose3D) -> str:
		"""Categorize pose orientation"""
		yaw = abs(pose['yaw'])
		pitch = abs(pose['pitch'])
		
		if yaw < 15 and pitch < 15:
			return 'frontal'
		elif yaw < 30:
			return 'slight_turn'
		elif yaw < 60:
			return 'profile'
		else:
			return 'extreme'
