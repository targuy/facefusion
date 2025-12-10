"""
Utilities for detecting face orientation from landmarks.

Calculates yaw, pitch, and roll from facial landmarks.
"""

import math
from typing import Optional, Tuple
import numpy as np


# Algorithm constants
EPSILON = 1e-6  # Small value to prevent division by zero

# Orientation scaling and clipping parameters
YAW_SCALE_FACTOR = 90.0  # Maximum yaw from asymmetry
YAW_CLIP_MIN = -90.0
YAW_CLIP_MAX = 90.0

PITCH_SCALE_FACTOR = 45.0  # Maximum pitch from nose position
PITCH_CLIP_MIN = -45.0
PITCH_CLIP_MAX = 45.0

# Default extreme orientation thresholds (degrees)
DEFAULT_MAX_YAW = 75.0
DEFAULT_MAX_PITCH = 45.0
DEFAULT_MAX_ROLL = 45.0


class OrientationDetector:
    """Detects face orientation from facial landmarks."""
    
    @staticmethod
    def calculate_orientation_from_landmarks(
        landmarks_68: np.ndarray,
        landmarks_5: Optional[np.ndarray] = None
    ) -> Tuple[float, float, float]:
        """
        Calculate yaw, pitch, and roll angles from face landmarks.
        
        Uses 68-point or 5-point landmarks to estimate head pose.
        
        Args:
            landmarks_68: 68-point facial landmarks (shape: 68x2)
            landmarks_5: Optional 5-point landmarks (shape: 5x2)
            
        Returns:
            Tuple of (yaw, pitch, roll) in degrees:
            - yaw: -180 to 180 (horizontal rotation, 0 is frontal)
            - pitch: -90 to 90 (vertical tilt, 0 is level)
            - roll: -180 to 180 (head tilt, 0 is upright)
        """
        # Check landmarks_68 first
        if landmarks_68 is not None:
            try:
                if hasattr(landmarks_68, '__len__') and len(landmarks_68) == 68:
                    return OrientationDetector._calculate_from_68_points(landmarks_68)
            except (TypeError, AttributeError):
                pass
        
        # Check landmarks_5 as fallback
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
        
        Uses key facial points:
        - Nose tip (30)
        - Left/right eye outer corners (36, 45)
        - Left/right mouth corners (48, 54)
        - Chin (8)
        """
        # Key landmark indices
        nose_tip = landmarks[30]
        chin = landmarks[8]
        left_eye = landmarks[36]
        right_eye = landmarks[45]
        left_mouth = landmarks[48]
        right_mouth = landmarks[54]
        
        # Calculate yaw (horizontal rotation)
        # Based on asymmetry of left/right eye distances from nose
        nose_to_left_eye = np.linalg.norm(nose_tip - left_eye)
        nose_to_right_eye = np.linalg.norm(nose_tip - right_eye)
        eye_asymmetry = (nose_to_left_eye - nose_to_right_eye) / (nose_to_left_eye + nose_to_right_eye + EPSILON)
        yaw = np.clip(eye_asymmetry * YAW_SCALE_FACTOR, YAW_CLIP_MIN, YAW_CLIP_MAX)
        
        # Calculate pitch (vertical tilt)
        # Based on nose-to-chin vertical distance relative to face height
        face_height = np.linalg.norm(landmarks[27] - chin)  # Eyebrow to chin
        nose_chin_y = nose_tip[1] - chin[1]
        pitch_ratio = nose_chin_y / (face_height + EPSILON)
        pitch = np.clip(pitch_ratio * PITCH_SCALE_FACTOR, PITCH_CLIP_MIN, PITCH_CLIP_MAX)
        
        # Calculate roll (head tilt)
        # Based on eye line angle
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
        yaw = np.clip(eye_asymmetry * YAW_SCALE_FACTOR, YAW_CLIP_MIN, YAW_CLIP_MAX)
        
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
        """
        Calculate roll angle from eye positions.
        
        Args:
            left_eye: Left eye position (x, y)
            right_eye: Right eye position (x, y)
            
        Returns:
            Roll angle in degrees
        """
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
        
        Args:
            yaw: Yaw angle in degrees
            pitch: Pitch angle in degrees
            roll: Roll angle in degrees
            
        Returns:
            Human-readable description (e.g., "Frontal", "Right Profile", "Looking Up")
        """
        descriptions = []
        
        # Yaw description
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
        
        # Pitch description
        if pitch > 20:
            descriptions.append("Looking Down")
        elif pitch < -20:
            descriptions.append("Looking Up")
        
        # Roll description
        if abs(roll) > 15:
            if roll > 0:
                descriptions.append("Tilted Right")
            else:
                descriptions.append("Tilted Left")
        
        if not descriptions:
            descriptions.append("Neutral")
        
        return ", ".join(descriptions)
