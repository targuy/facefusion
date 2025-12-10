"""
Automatic face orientation detection from facial landmarks.

Combines automatic detection with validation thresholds to ensure quality.
Detects yaw, pitch, and roll using geometric analysis of facial landmarks.
"""

import math
from typing import Optional, Tuple
import numpy as np

# Validation thresholds from PR #16
DEFAULT_MAX_YAW = 75.0
DEFAULT_MAX_PITCH = 45.0
DEFAULT_MAX_ROLL = 45.0

# Algorithm constants
EPSILON = 1e-6
YAW_SCALE_FACTOR = 90.0
PITCH_SCALE_FACTOR = 45.0

# 68-point landmark indices (dlib format)
LANDMARK_NOSE_TIP = 30
LANDMARK_CHIN = 8
LANDMARK_LEFT_EYE_OUTER = 36
LANDMARK_RIGHT_EYE_OUTER = 45
LANDMARK_LEFT_MOUTH = 48
LANDMARK_RIGHT_MOUTH = 54
LANDMARK_EYEBROW_TOP = 27


class OrientationDetector:
    """Detects face orientation automatically from facial landmarks."""
    
    @staticmethod
    def calculate_orientation_from_landmarks(
        landmarks_68: Optional[np.ndarray],
        landmarks_5: Optional[np.ndarray] = None
    ) -> Tuple[float, float, float]:
        """
        Calculate yaw, pitch, and roll angles from face landmarks.
        
        Uses 68-point or 5-point landmarks to estimate head pose.
        Automatically validates orientation is within acceptable ranges.
        
        Args:
            landmarks_68: 68-point facial landmarks (shape: 68x2)
            landmarks_5: Optional 5-point landmarks (shape: 5x2)
            
        Returns:
            Tuple of (yaw, pitch, roll) in degrees:
            - yaw: -180 to 180 (horizontal rotation, 0 is frontal)
            - pitch: -90 to 90 (vertical tilt, 0 is level)
            - roll: -180 to 180 (head tilt, 0 is upright)
        """
        # Try 68-point landmarks first
        if landmarks_68 is not None:
            try:
                if hasattr(landmarks_68, '__len__') and len(landmarks_68) == 68:
                    return OrientationDetector._calculate_from_68_points(landmarks_68)
            except (TypeError, AttributeError):
                pass
        
        # Fallback to 5-point landmarks
        if landmarks_5 is not None:
            try:
                if hasattr(landmarks_5, '__len__') and len(landmarks_5) == 5:
                    return OrientationDetector._calculate_from_5_points(landmarks_5)
            except (TypeError, AttributeError):
                pass
        
        # Default to frontal if no valid landmarks
        return (0.0, 0.0, 0.0)
    
    @staticmethod
    def _calculate_from_68_points(landmarks: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate orientation from 68-point landmarks.
        
        Uses key facial points for accurate pose estimation.
        """
        # Extract key landmarks using named constants
        nose_tip = landmarks[LANDMARK_NOSE_TIP]
        chin = landmarks[LANDMARK_CHIN]
        left_eye = landmarks[LANDMARK_LEFT_EYE_OUTER]
        right_eye = landmarks[LANDMARK_RIGHT_EYE_OUTER]
        left_mouth = landmarks[LANDMARK_LEFT_MOUTH]
        right_mouth = landmarks[LANDMARK_RIGHT_MOUTH]
        
        # Calculate yaw (horizontal rotation) from eye-nose asymmetry
        nose_to_left_eye = np.linalg.norm(nose_tip - left_eye)
        nose_to_right_eye = np.linalg.norm(nose_tip - right_eye)
        eye_asymmetry = (nose_to_left_eye - nose_to_right_eye) / (nose_to_left_eye + nose_to_right_eye + EPSILON)
        yaw = np.clip(eye_asymmetry * YAW_SCALE_FACTOR, -90, 90)
        
        # Calculate pitch (vertical tilt) from nose position
        face_height = np.linalg.norm(landmarks[LANDMARK_EYEBROW_TOP] - chin)
        nose_chin_y = nose_tip[1] - chin[1]
        pitch_ratio = nose_chin_y / (face_height + EPSILON)
        pitch = np.clip(pitch_ratio * PITCH_SCALE_FACTOR, -45, 45)
        
        # Calculate roll (head tilt) from eye line angle
        roll = OrientationDetector._calculate_roll_from_eyes(left_eye, right_eye)
        
        return (float(yaw), float(pitch), float(roll))
    
    @staticmethod
    def _calculate_from_5_points(landmarks: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate orientation from 5-point landmarks.
        
        Points: left_eye, right_eye, nose, left_mouth, right_mouth
        """
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        nose = landmarks[2]
        left_mouth = landmarks[3]
        right_mouth = landmarks[4]
        
        # Calculate yaw from eye-nose distances
        nose_to_left_eye = np.linalg.norm(nose - left_eye)
        nose_to_right_eye = np.linalg.norm(nose - right_eye)
        eye_asymmetry = (nose_to_left_eye - nose_to_right_eye) / (nose_to_left_eye + nose_to_right_eye + EPSILON)
        yaw = np.clip(eye_asymmetry * YAW_SCALE_FACTOR, -90, 90)
        
        # Calculate pitch from nose-mouth vertical distance
        eye_center = (left_eye + right_eye) / 2
        mouth_center = (left_mouth + right_mouth) / 2
        face_height = np.linalg.norm(eye_center - mouth_center)
        nose_mouth_y = nose[1] - mouth_center[1]
        pitch_ratio = nose_mouth_y / (face_height + EPSILON)
        pitch = np.clip(pitch_ratio * 30, -30, 30)
        
        # Calculate roll from eye line angle
        roll = OrientationDetector._calculate_roll_from_eyes(left_eye, right_eye)
        
        return (float(yaw), float(pitch), float(roll))
    
    @staticmethod
    def _calculate_roll_from_eyes(left_eye: np.ndarray, right_eye: np.ndarray) -> float:
        """Calculate roll angle from eye positions."""
        eye_vector = right_eye - left_eye
        return float(math.degrees(math.atan2(eye_vector[1], eye_vector[0])))
    
    @staticmethod
    def is_extreme_orientation(
        yaw: float,
        pitch: float,
        roll: float,
        max_yaw: float = DEFAULT_MAX_YAW,
        max_pitch: float = DEFAULT_MAX_PITCH,
        max_roll: float = DEFAULT_MAX_ROLL
    ) -> bool:
        """
        Check if face orientation is too extreme (face not properly visible).
        
        Validates that face is within acceptable viewing angles for face swapping.
        
        Args:
            yaw: Yaw angle in degrees
            pitch: Pitch angle in degrees
            roll: Roll angle in degrees
            max_yaw: Maximum acceptable yaw (default 75 degrees)
            max_pitch: Maximum acceptable pitch (default 45 degrees)
            max_roll: Maximum acceptable roll (default 45 degrees)
            
        Returns:
            True if orientation is too extreme and should be rejected
        """
        return (
            abs(yaw) > max_yaw or
            abs(pitch) > max_pitch or
            abs(roll) > max_roll
        )
    
    @staticmethod
    def get_orientation_description(yaw: float, pitch: float, roll: float) -> str:
        """
        Get human-readable description of face orientation.
        
        Provides clear feedback about detected orientation for user understanding.
        
        Args:
            yaw: Yaw angle in degrees
            pitch: Pitch angle in degrees
            roll: Roll angle in degrees
            
        Returns:
            Human-readable description (e.g., "Frontal", "Right Profile, Looking Up")
        """
        descriptions = []
        
        # Yaw description (horizontal)
        if abs(yaw) < 15:
            descriptions.append("Frontal")
        elif yaw > 60:
            descriptions.append("Right Profile")
        elif yaw > 30:
            descriptions.append("Right Quarter")
        elif yaw < -60:
            descriptions.append("Left Profile")
        elif yaw < -30:
            descriptions.append("Left Quarter")
        
        # Pitch description (vertical)
        if pitch > 20:
            descriptions.append("Looking Down")
        elif pitch < -20:
            descriptions.append("Looking Up")
        
        # Roll description (tilt)
        if abs(roll) > 15:
            if roll > 0:
                descriptions.append("Tilted Right")
            else:
                descriptions.append("Tilted Left")
        
        if not descriptions:
            descriptions.append("Neutral")
        
        return ", ".join(descriptions)
