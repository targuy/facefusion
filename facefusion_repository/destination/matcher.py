"""
Repository face matching for destination faces.

Matches destination faces with repository faces based on orientation similarity,
quality metrics, and compatibility.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np

from facefusion.types import Face
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.repository.orientation_matcher import OrientationMatcher
from facefusion_repository.types import FaceEntry, QualityMetrics


class FaceMatch:
    """Represents a match between destination face and repository face."""

    def __init__(
        self,
        destination_face: Face,
        repository_face: FaceEntry,
        confidence: float,
        orientation_difference: int
    ):
        """
        Initialize face match.

        Args:
            destination_face: Detected face from destination
            repository_face: Matching face from repository
            confidence: Match confidence score (0.0-1.0)
            orientation_difference: Angle difference in degrees
        """
        self.destination_face = destination_face
        self.repository_face = repository_face
        self.confidence = confidence
        self.orientation_difference = orientation_difference


class RepositoryMatcher:
    """Matches destination faces with repository faces."""

    def __init__(self, repository_manager: RepositoryManager):
        """
        Initialize repository matcher.

        Args:
            repository_manager: Repository manager instance
        """
        self.repository_manager = repository_manager

    def find_best_match(
        self,
        destination_face: Face,
        destination_quality: QualityMetrics,
        orientation_tolerance: int = 22
    ) -> Optional[FaceMatch]:
        """
        Find the best matching repository face for a destination face.

        Args:
            destination_face: Face detected in destination media
            destination_quality: Quality metrics of destination face
            orientation_tolerance: Maximum angle difference in degrees

        Returns:
            FaceMatch object if match found, None otherwise
        """
        # Get destination face orientation
        dest_angle = OrientationMatcher.get_closest_standard_angle(destination_face.angle)

        # Get all repository faces
        repo_faces = self.repository_manager.list_faces()
        if not repo_faces:
            return None

        # Find faces with similar orientation
        candidates = []
        for repo_face in repo_faces:
            if OrientationMatcher.is_orientation_similar(
                dest_angle,
                repo_face.orientation_angle,
                threshold=orientation_tolerance
            ):
                angle_diff = abs(dest_angle - repo_face.orientation_angle)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff

                # Calculate confidence based on orientation match and quality
                orientation_confidence = 1.0 - (angle_diff / orientation_tolerance)
                quality_confidence = (
                    repo_face.quality_metrics.overall_quality * 0.5 +
                    destination_quality.overall_quality * 0.5
                )
                confidence = (orientation_confidence * 0.6 + quality_confidence * 0.4)

                candidates.append((repo_face, confidence, angle_diff))

        if not candidates:
            return None

        # Select best candidate (highest confidence)
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_repo_face, best_confidence, angle_diff = candidates[0]

        return FaceMatch(
            destination_face=destination_face,
            repository_face=best_repo_face,
            confidence=best_confidence,
            orientation_difference=angle_diff
        )

    def find_all_matches(
        self,
        destination_faces: List[Tuple[Face, QualityMetrics]],
        orientation_tolerance: int = 22,
        min_confidence: float = 0.5
    ) -> List[FaceMatch]:
        """
        Find matches for multiple destination faces.

        Args:
            destination_faces: List of (face, quality_metrics) tuples
            orientation_tolerance: Maximum angle difference in degrees
            min_confidence: Minimum confidence threshold

        Returns:
            List of FaceMatch objects
        """
        matches = []

        for dest_face, dest_quality in destination_faces:
            match = self.find_best_match(
                dest_face,
                dest_quality,
                orientation_tolerance=orientation_tolerance
            )

            if match and match.confidence >= min_confidence:
                matches.append(match)

        return matches

    def get_match_statistics(
        self,
        matches: List[FaceMatch]
    ) -> Dict[str, any]:
        """
        Get statistics about face matches.

        Args:
            matches: List of face matches

        Returns:
            Dictionary with match statistics
        """
        if not matches:
            return {
                'total_matches': 0,
                'average_confidence': 0.0,
                'matches_by_face': {},
                'average_orientation_diff': 0.0
            }

        # Group matches by repository face
        matches_by_face: Dict[str, List[FaceMatch]] = {}
        for match in matches:
            face_id = match.repository_face.id
            if face_id not in matches_by_face:
                matches_by_face[face_id] = []
            matches_by_face[face_id].append(match)

        # Calculate statistics
        total_confidence = sum(m.confidence for m in matches)
        total_angle_diff = sum(m.orientation_difference for m in matches)

        return {
            'total_matches': len(matches),
            'average_confidence': total_confidence / len(matches),
            'matches_by_face': {
                face_id: len(face_matches)
                for face_id, face_matches in matches_by_face.items()
            },
            'average_orientation_diff': total_angle_diff / len(matches),
            'unique_repository_faces': len(matches_by_face)
        }
