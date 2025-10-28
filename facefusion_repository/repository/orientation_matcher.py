"""
Orientation matching for face repository system.
"""

from typing import List, Optional

from facefusion_repository.types import FaceEntry


class OrientationMatcher:
    """Matches faces based on orientation angles."""

    # Standard orientation angles (8 directions)
    STANDARD_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]

    @staticmethod
    def normalize_angle(angle: int) -> int:
        """
        Normalize angle to 0-360 range.

        Args:
            angle: Input angle (can be negative or > 360)

        Returns:
            Normalized angle in 0-360 range
        """
        return angle % 360

    @staticmethod
    def get_closest_standard_angle(angle: int) -> int:
        """
        Map angle to closest standard angle.

        Args:
            angle: Input angle

        Returns:
            Closest standard angle (0, 45, 90, 135, 180, 225, 270, 315)
        """
        angle = OrientationMatcher.normalize_angle(angle)

        # Find closest standard angle
        min_diff = 360
        closest = 0

        for std_angle in OrientationMatcher.STANDARD_ANGLES:
            diff = OrientationMatcher.calculate_angle_distance(angle, std_angle)
            if diff < min_diff:
                min_diff = diff
                closest = std_angle

        return closest

    @staticmethod
    def calculate_angle_distance(angle1: int, angle2: int) -> int:
        """
        Calculate minimum angular distance between two angles.

        Args:
            angle1: First angle
            angle2: Second angle

        Returns:
            Minimum angular distance (0-180)
        """
        angle1 = OrientationMatcher.normalize_angle(angle1)
        angle2 = OrientationMatcher.normalize_angle(angle2)

        # Calculate both clockwise and counter-clockwise distances
        diff = abs(angle1 - angle2)

        # Return minimum distance
        return min(diff, 360 - diff)

    @staticmethod
    def find_best_match(
        target_angle: int,
        candidates: List[FaceEntry],
        max_angle_diff: int = 45
    ) -> Optional[FaceEntry]:
        """
        Find best matching face based on orientation.

        Args:
            target_angle: Target orientation angle
            candidates: List of candidate face entries
            max_angle_diff: Maximum acceptable angle difference

        Returns:
            Best matching FaceEntry or None if no acceptable match
        """
        if not candidates:
            return None

        best_match = None
        best_distance = max_angle_diff + 1

        for candidate in candidates:
            distance = OrientationMatcher.calculate_angle_distance(
                target_angle,
                candidate.orientation_angle
            )

            if distance < best_distance:
                best_distance = distance
                best_match = candidate

        # Return None if best match exceeds threshold
        if best_distance > max_angle_diff:
            return None

        return best_match

    @staticmethod
    def is_orientation_similar(angle1: int, angle2: int, threshold: int = 15) -> bool:
        """
        Check if two orientations are similar enough to be considered duplicates.

        Args:
            angle1: First angle
            angle2: Second angle
            threshold: Maximum difference for similarity

        Returns:
            True if angles are similar within threshold
        """
        distance = OrientationMatcher.calculate_angle_distance(angle1, angle2)
        return distance <= threshold

    @staticmethod
    def group_by_orientation(
        faces: List[FaceEntry],
        tolerance: int = 45
    ) -> dict[int, List[FaceEntry]]:
        """
        Group faces by similar orientations.

        Args:
            faces: List of face entries
            tolerance: Angle tolerance for grouping

        Returns:
            Dictionary mapping standard angles to lists of faces
        """
        groups: dict[int, List[FaceEntry]] = {angle: [] for angle in OrientationMatcher.STANDARD_ANGLES}

        for face in faces:
            # Find closest standard angle
            closest = OrientationMatcher.get_closest_standard_angle(face.orientation_angle)

            # Only add if within tolerance
            if OrientationMatcher.calculate_angle_distance(face.orientation_angle, closest) <= tolerance:
                groups[closest].append(face)

        return groups

    @staticmethod
    def get_best_quality_face(faces: List[FaceEntry]) -> Optional[FaceEntry]:
        """
        Get the highest quality face from a list.

        Args:
            faces: List of face entries

        Returns:
            Face with highest overall quality, or None if list is empty
        """
        if not faces:
            return None

        return max(faces, key=lambda f: f.quality_metrics.overall_quality)
