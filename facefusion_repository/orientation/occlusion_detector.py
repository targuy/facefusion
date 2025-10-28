"""
Occlusion detection for facial landmarks.
"""

import numpy as np
from typing import List, Set

from facefusion.types import Face
from facefusion_repository.types import OcclusionInfo


class OcclusionDetector:
    """Detects facial occlusions that may affect face recognition quality."""

    # Landmark groups for different facial regions (68-point model)
    LANDMARK_GROUPS = {
        'left_eye': list(range(36, 42)),
        'right_eye': list(range(42, 48)),
        'nose': list(range(27, 36)),
        'mouth': list(range(48, 68)),
        'jaw': list(range(0, 17)),
        'left_eyebrow': list(range(17, 22)),
        'right_eyebrow': list(range(22, 27))
    }

    # Critical landmarks that must be visible for good face recognition
    CRITICAL_LANDMARKS = ['left_eye', 'right_eye', 'nose']

    @staticmethod
    def detect_occlusion(face: Face, image_shape: tuple) -> OcclusionInfo:
        """
        Detect occlusions in facial landmarks.

        Args:
            face: Face object with landmarks
            image_shape: Shape of the image (height, width)

        Returns:
            OcclusionInfo object with occlusion details
        """
        if '68' not in face.landmark_set:
            # Cannot detect occlusion without 68-point landmarks
            return OcclusionInfo(
                score=0.5,  # Unknown occlusion
                occluded_landmarks=[],
                is_usable=True
            )

        landmarks_68 = face.landmark_set['68']
        bbox = face.bounding_box

        # Detect occluded landmark groups
        occluded_groups = OcclusionDetector._detect_occluded_groups(landmarks_68, bbox, image_shape)

        # Calculate occlusion score (0 = no occlusion, 1 = fully occluded)
        total_groups = len(OcclusionDetector.LANDMARK_GROUPS)
        occluded_count = len(occluded_groups)
        occlusion_score = occluded_count / total_groups

        # Check if critical regions are occluded
        critical_occluded = any(
            group in occluded_groups 
            for group in OcclusionDetector.CRITICAL_LANDMARKS
        )

        # Face is usable if no critical regions are occluded
        is_usable = not critical_occluded

        return OcclusionInfo(
            score=float(occlusion_score),
            occluded_landmarks=list(occluded_groups),
            is_usable=is_usable
        )

    @staticmethod
    def _detect_occluded_groups(landmarks: np.ndarray, bbox: tuple, image_shape: tuple) -> Set[str]:
        """
        Detect which landmark groups are occluded.

        Args:
            landmarks: 68 facial landmark points
            bbox: Face bounding box
            image_shape: Image dimensions

        Returns:
            Set of occluded landmark group names
        """
        occluded_groups = set()

        image_height, image_width = image_shape[:2]

        for group_name, indices in OcclusionDetector.LANDMARK_GROUPS.items():
            # Check if landmarks are out of bounds
            group_landmarks = landmarks[indices]

            # Check if landmarks are outside image bounds
            out_of_bounds = (
                np.any(group_landmarks[:, 0] < 0) or
                np.any(group_landmarks[:, 0] >= image_width) or
                np.any(group_landmarks[:, 1] < 0) or
                np.any(group_landmarks[:, 1] >= image_height)
            )

            if out_of_bounds:
                occluded_groups.add(group_name)
                continue

            # Check if landmarks are clustered too tightly (indicating occlusion)
            if len(group_landmarks) > 2:
                std_x = np.std(group_landmarks[:, 0])
                std_y = np.std(group_landmarks[:, 1])

                # If standard deviation is very low, landmarks might be occluded
                # and the detector placed them at default positions
                bbox_width = bbox[2] - bbox[0]
                bbox_height = bbox[3] - bbox[1]

                expected_spread = min(bbox_width, bbox_height) * 0.02

                if std_x < expected_spread or std_y < expected_spread:
                    occluded_groups.add(group_name)
                    continue

            # Check for unusual landmark positions relative to face bbox
            # If landmarks are too close to bbox edge, they might be occluded
            bbox_margin = 5  # pixels

            near_edge = (
                np.any(group_landmarks[:, 0] < bbox[0] + bbox_margin) or
                np.any(group_landmarks[:, 0] > bbox[2] - bbox_margin) or
                np.any(group_landmarks[:, 1] < bbox[1] + bbox_margin) or
                np.any(group_landmarks[:, 1] > bbox[3] - bbox_margin)
            )

            if near_edge:
                # Additional check: if multiple points are near edge, likely occluded
                edge_count = sum([
                    np.sum(group_landmarks[:, 0] < bbox[0] + bbox_margin),
                    np.sum(group_landmarks[:, 0] > bbox[2] - bbox_margin),
                    np.sum(group_landmarks[:, 1] < bbox[1] + bbox_margin),
                    np.sum(group_landmarks[:, 1] > bbox[3] - bbox_margin)
                ])

                if edge_count >= len(group_landmarks) * 0.5:
                    occluded_groups.add(group_name)

        return occluded_groups

    @staticmethod
    def is_face_usable(occlusion_info: OcclusionInfo, max_occlusion_score: float = 0.3) -> bool:
        """
        Check if face is usable despite occlusion.

        Args:
            occlusion_info: OcclusionInfo object
            max_occlusion_score: Maximum acceptable occlusion score

        Returns:
            True if face is usable
        """
        # Face is usable if:
        # 1. Critical landmarks are not occluded
        # 2. Overall occlusion score is below threshold
        return (
            occlusion_info.is_usable and 
            occlusion_info.score <= max_occlusion_score
        )

    @staticmethod
    def get_occlusion_summary(occlusion_info: OcclusionInfo) -> str:
        """
        Get human-readable summary of occlusion.

        Args:
            occlusion_info: OcclusionInfo object

        Returns:
            Summary string
        """
        if occlusion_info.score == 0:
            return "No occlusion detected"

        if not occlusion_info.is_usable:
            return f"Critical occlusion detected: {', '.join(occlusion_info.occluded_landmarks)}"

        if occlusion_info.score < 0.3:
            return f"Minor occlusion: {', '.join(occlusion_info.occluded_landmarks)}"

        return f"Moderate occlusion: {', '.join(occlusion_info.occluded_landmarks)}"
