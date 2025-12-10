"""
3D orientation detection for faces using landmarks.
Calculates yaw, pitch, and roll from facial landmarks.
"""

import math
from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from facefusion_repository.types import Orientation3D


class Orientation3DDetector:
    """Detects 3D orientation (yaw, pitch, roll) from face landmarks."""
    
    # Model points for face key landmarks (normalized 3D model)
    # Based on canonical 3D face model
    MODEL_POINTS = np.array([
        (0.0, 0.0, 0.0),          # Nose tip
        (0.0, -330.0, -65.0),     # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),   # Right eye right corner
        (-150.0, -150.0, -125.0), # Left mouth corner
        (150.0, -150.0, -125.0)   # Right mouth corner
    ], dtype=np.float64)
    
    @staticmethod
    def detect_from_landmarks(landmarks: dict) -> Optional[Orientation3D]:
        """
        Detect 3D orientation from face landmarks.
        
        Args:
            landmarks: Dictionary containing face landmarks from FaceFusion
            
        Returns:
            Orientation3D object with yaw, pitch, roll angles in degrees,
            or None if detection fails
        """
        try:
            # Extract key landmark points from FaceFusion format
            # FaceFusion stores landmarks in a specific format
            if not landmarks or 'landmarks' not in landmarks:
                return None
            
            landmark_data = landmarks['landmarks']
            
            # Extract 6 key points needed for orientation estimation
            # Points: nose_tip, chin, left_eye_left, right_eye_right, left_mouth, right_mouth
            image_points = Orientation3DDetector._extract_key_points(landmark_data)
            
            if image_points is None:
                return None
            
            # Calculate orientation using PnP (Perspective-n-Point)
            yaw, pitch, roll = Orientation3DDetector._calculate_angles(image_points)
            
            return Orientation3D(yaw=yaw, pitch=pitch, roll=roll)
            
        except Exception as e:
            print(f"Error detecting 3D orientation: {e}")
            return None
    
    @staticmethod
    def _extract_key_points(landmark_data: any) -> Optional[NDArray[np.float64]]:
        """
        Extract key landmark points from FaceFusion landmark data.
        
        Args:
            landmark_data: Landmark data from FaceFusion
            
        Returns:
            Numpy array of 6 key points (x, y) coordinates, or None if extraction fails
        """
        try:
            # FaceFusion stores 68 or 5-point landmarks
            # We need to extract the 6 key points for orientation
            
            if isinstance(landmark_data, np.ndarray):
                # Assuming 68-point or 5-point landmark format
                if len(landmark_data) >= 68:
                    # 68-point format (dlib style)
                    points = np.array([
                        landmark_data[30],  # Nose tip (point 30)
                        landmark_data[8],   # Chin (point 8)
                        landmark_data[36],  # Left eye left corner (point 36)
                        landmark_data[45],  # Right eye right corner (point 45)
                        landmark_data[48],  # Left mouth corner (point 48)
                        landmark_data[54]   # Right mouth corner (point 54)
                    ], dtype=np.float64)
                    return points
                elif len(landmark_data) == 5:
                    # 5-point format - estimate the 6 points
                    # Points: left_eye, right_eye, nose, left_mouth, right_mouth
                    left_eye = landmark_data[0]
                    right_eye = landmark_data[1]
                    nose = landmark_data[2]
                    left_mouth = landmark_data[3]
                    right_mouth = landmark_data[4]
                    
                    # Estimate chin as below nose
                    chin = nose + np.array([0, abs(nose[1] - left_mouth[1]) * 0.8])
                    
                    points = np.array([
                        nose,
                        chin,
                        left_eye,
                        right_eye,
                        left_mouth,
                        right_mouth
                    ], dtype=np.float64)
                    return points
            
            return None
            
        except Exception as e:
            print(f"Error extracting key points: {e}")
            return None
    
    @staticmethod
    def _calculate_angles(image_points: NDArray[np.float64]) -> Tuple[float, float, float]:
        """
        Calculate yaw, pitch, roll from 2D image points using simplified method.
        
        Args:
            image_points: 2D coordinates of 6 key facial landmarks
            
        Returns:
            Tuple of (yaw, pitch, roll) in degrees
        """
        try:
            # Simplified angle calculation based on landmark positions
            # More accurate than just horizontal angle
            
            # Extract key points
            nose = image_points[0]
            chin = image_points[1]
            left_eye = image_points[2]
            right_eye = image_points[3]
            left_mouth = image_points[4]
            right_mouth = image_points[5]
            
            # Calculate eye center and mouth center
            eye_center = (left_eye + right_eye) / 2
            mouth_center = (left_mouth + right_mouth) / 2
            
            # Calculate yaw (horizontal rotation)
            # Based on the asymmetry of eye positions relative to nose
            eye_line_length = np.linalg.norm(right_eye - left_eye)
            left_eye_to_nose = np.linalg.norm(left_eye - nose)
            right_eye_to_nose = np.linalg.norm(right_eye - nose)
            
            # Yaw calculation
            if eye_line_length > 0:
                yaw_ratio = (right_eye_to_nose - left_eye_to_nose) / eye_line_length
                yaw = np.clip(yaw_ratio * 90, -90, 90)  # Scale to -90 to 90 degrees
            else:
                yaw = 0.0
            
            # Calculate pitch (vertical tilt)
            # Based on the vertical position of features
            face_height = np.linalg.norm(chin - eye_center)
            nose_to_eye_dist = np.linalg.norm(nose - eye_center)
            
            if face_height > 0:
                pitch_ratio = (nose_to_eye_dist / face_height) - 0.3  # Normalized baseline
                pitch = np.clip(pitch_ratio * 100, -45, 45)  # Scale to -45 to 45 degrees
            else:
                pitch = 0.0
            
            # Calculate roll (head tilt)
            # Based on the angle of the eye line
            eye_vector = right_eye - left_eye
            roll = math.degrees(math.atan2(eye_vector[1], eye_vector[0]))
            # Normalize to -180 to 180
            if roll > 180:
                roll -= 360
            elif roll < -180:
                roll += 360
            
            return float(yaw), float(pitch), float(roll)
            
        except Exception as e:
            print(f"Error calculating angles: {e}")
            return 0.0, 0.0, 0.0
    
    @staticmethod
    def get_primary_orientation_angle(orientation_3d: Orientation3D) -> int:
        """
        Get the primary horizontal orientation angle (0-360) from 3D orientation.
        Maps to legacy orientation_angle format (0, 45, 90, 135, 180, 225, 270, 315).
        
        Args:
            orientation_3d: 3D orientation object
            
        Returns:
            Primary orientation angle in degrees (0-360)
        """
        # Use yaw as the primary angle, normalized to 0-360
        angle = orientation_3d.yaw
        if angle < 0:
            angle += 360
        
        # Round to nearest 45 degrees for standard angles
        standard_angles = [0, 45, 90, 135, 180, 225, 270, 315]
        return min(standard_angles, key=lambda x: abs(x - angle))
    
    @staticmethod
    def calculate_3d_distance(orient1: Orientation3D, orient2: Orientation3D) -> float:
        """
        Calculate the angular distance between two 3D orientations.
        
        Args:
            orient1: First orientation
            orient2: Second orientation
            
        Returns:
            Combined angular distance (weighted sum of differences)
        """
        # Normalize angles to -180 to 180 range for distance calculation
        def normalize_angle(angle: float) -> float:
            while angle > 180:
                angle -= 360
            while angle < -180:
                angle += 360
            return angle
        
        yaw_diff = abs(normalize_angle(orient1.yaw - orient2.yaw))
        pitch_diff = abs(normalize_angle(orient1.pitch - orient2.pitch))
        roll_diff = abs(normalize_angle(orient1.roll - orient2.roll))
        
        # Weighted combination: yaw is most important, then pitch, then roll
        weighted_distance = (yaw_diff * 1.0) + (pitch_diff * 0.5) + (roll_diff * 0.3)
        
        return weighted_distance
