"""
3D pose estimation from facial landmarks.
"""

import math
import numpy as np
from typing import Dict, Optional

from facefusion.types import Face
from facefusion_repository.types import Pose3D


class PoseEstimator:
    """Estimates 3D head pose from facial landmarks."""

    # 3D model points for standard face landmarks (in normalized coordinates)
    # These are approximate 3D coordinates for key facial points
    MODEL_POINTS_68 = np.array([
        (0.0, 0.0, 0.0),              # Nose tip (30)
        (0.0, -330.0, -65.0),         # Chin (8)
        (-225.0, 170.0, -135.0),      # Left eye left corner (36)
        (225.0, 170.0, -135.0),       # Right eye right corner (45)
        (-150.0, -150.0, -125.0),     # Left mouth corner (48)
        (150.0, -150.0, -125.0)       # Right mouth corner (54)
    ])

    # Corresponding 2D landmark indices for 68-point model
    LANDMARK_INDICES_68 = [30, 8, 36, 45, 48, 54]

    @staticmethod
    def estimate_pose(face: Face) -> Optional[Pose3D]:
        """
        Estimate 3D head pose from facial landmarks.

        Args:
            face: Face object with landmarks

        Returns:
            Pose3D object or None if estimation fails
        """
        try:
            # Get 68-point landmarks
            if '68' not in face.landmark_set:
                return None

            landmarks_68 = face.landmark_set['68']

            # Extract specific landmark points
            image_points = np.array([
                landmarks_68[idx] for idx in PoseEstimator.LANDMARK_INDICES_68
            ], dtype=np.float64)

            # Estimate camera parameters (focal length based on image size)
            # Assume image center at bounding box center
            bbox = face.bounding_box
            image_width = bbox[2] - bbox[0]
            image_height = bbox[3] - bbox[1]
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2

            # Focal length approximation
            focal_length = max(image_width, image_height)

            # Camera matrix
            camera_matrix = np.array([
                [focal_length, 0, center_x],
                [0, focal_length, center_y],
                [0, 0, 1]
            ], dtype=np.float64)

            # Assume no lens distortion
            dist_coeffs = np.zeros((4, 1))

            # Solve PnP to get rotation and translation vectors
            try:
                import cv2
                success, rotation_vector, translation_vector = cv2.solvePnP(
                    PoseEstimator.MODEL_POINTS_68,
                    image_points,
                    camera_matrix,
                    dist_coeffs,
                    flags=cv2.SOLVEPNP_ITERATIVE
                )

                if not success:
                    return None

                # Convert rotation vector to rotation matrix
                rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

                # Extract Euler angles from rotation matrix
                pitch, yaw, tilt = PoseEstimator._rotation_matrix_to_euler_angles(rotation_matrix)

                # Calculate confidence based on reprojection error
                projected_points, _ = cv2.projectPoints(
                    PoseEstimator.MODEL_POINTS_68,
                    rotation_vector,
                    translation_vector,
                    camera_matrix,
                    dist_coeffs
                )

                # Calculate reprojection error
                error = np.linalg.norm(image_points - projected_points.reshape(-1, 2), axis=1).mean()

                # Normalize error to confidence (lower error = higher confidence)
                # Typical error range is 0-20 pixels
                confidence = max(0.0, min(1.0, 1.0 - (error / 20.0)))

                return Pose3D(
                    pitch=float(pitch),
                    yaw=float(yaw),
                    tilt=float(tilt),
                    confidence=float(confidence)
                )

            except ImportError:
                # cv2 not available, use simplified estimation from landmarks
                return PoseEstimator._simple_pose_estimation(landmarks_68)

        except Exception as e:
            print(f'Warning: Could not estimate pose: {e}')
            return None

    @staticmethod
    def _rotation_matrix_to_euler_angles(R: np.ndarray) -> tuple:
        """
        Convert rotation matrix to Euler angles (pitch, yaw, tilt).

        Args:
            R: 3x3 rotation matrix

        Returns:
            Tuple of (pitch, yaw, tilt) in degrees
        """
        # Calculate Euler angles from rotation matrix
        sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

        singular = sy < 1e-6

        if not singular:
            pitch = math.atan2(R[2, 1], R[2, 2])
            yaw = math.atan2(-R[2, 0], sy)
            tilt = math.atan2(R[1, 0], R[0, 0])
        else:
            pitch = math.atan2(-R[1, 2], R[1, 1])
            yaw = math.atan2(-R[2, 0], sy)
            tilt = 0

        # Convert from radians to degrees
        pitch = math.degrees(pitch)
        yaw = math.degrees(yaw)
        tilt = math.degrees(tilt)

        return pitch, yaw, tilt

    @staticmethod
    def _simple_pose_estimation(landmarks_68: np.ndarray) -> Pose3D:
        """
        Simple pose estimation from landmarks without cv2.

        Args:
            landmarks_68: 68 facial landmark points

        Returns:
            Pose3D object with estimated angles
        """
        # Simple estimation based on landmark positions
        # This is less accurate but doesn't require cv2.solvePnP

        # Calculate face center
        face_center = np.mean(landmarks_68, axis=0)

        # Estimate yaw from nose position relative to eye center
        left_eye = landmarks_68[36]
        right_eye = landmarks_68[45]
        nose_tip = landmarks_68[30]

        eye_center = (left_eye + right_eye) / 2
        nose_offset = nose_tip[0] - eye_center[0]
        eye_distance = np.linalg.norm(right_eye - left_eye)

        # Normalize and convert to yaw angle
        yaw = (nose_offset / eye_distance) * 45.0  # Approximate scaling

        # Estimate pitch from nose position relative to eye-mouth line
        mouth_center = (landmarks_68[48] + landmarks_68[54]) / 2
        vertical_distance = eye_center[1] - mouth_center[1]
        nose_vertical_offset = nose_tip[1] - eye_center[1]

        # Normalize and convert to pitch angle
        if vertical_distance != 0:
            pitch = (nose_vertical_offset / vertical_distance) * 30.0  # Approximate scaling
        else:
            pitch = 0.0

        # Estimate tilt from eye line angle
        eye_angle = math.atan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0])
        tilt = math.degrees(eye_angle)

        # Low confidence for simple estimation
        confidence = 0.5

        return Pose3D(
            pitch=float(pitch),
            yaw=float(yaw),
            tilt=float(tilt),
            confidence=float(confidence)
        )

    @staticmethod
    def is_pose_acceptable(pose: Pose3D, max_pitch: float = 30.0, max_yaw: float = 45.0, max_tilt: float = 20.0) -> bool:
        """
        Check if pose is within acceptable ranges for face recognition.

        Args:
            pose: Pose3D object
            max_pitch: Maximum acceptable pitch angle
            max_yaw: Maximum acceptable yaw angle
            max_tilt: Maximum acceptable tilt angle

        Returns:
            True if pose is acceptable
        """
        if abs(pose.pitch) > max_pitch:
            return False
        if abs(pose.yaw) > max_yaw:
            return False
        if abs(pose.tilt) > max_tilt:
            return False

        return True

    @staticmethod
    def get_orientation_angle_from_pose(pose: Pose3D) -> int:
        """
        Convert 3D pose to 2D orientation angle (for backward compatibility).

        Args:
            pose: Pose3D object

        Returns:
            Orientation angle in degrees (0-360)
        """
        # Primary orientation is based on yaw
        # Normalize yaw to 0-360 range
        angle = pose.yaw % 360

        # Adjust angle to nearest standard angle (0, 45, 90, etc.)
        standard_angles = [0, 45, 90, 135, 180, 225, 270, 315]
        closest_angle = min(standard_angles, key=lambda x: abs(angle - x))

        return closest_angle
