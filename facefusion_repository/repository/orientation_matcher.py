"""
Orientation matching for face selection.

Matches destination face orientations with repository faces to find
the best source face for each swap operation.
"""

from typing import List, Optional
import math

from facefusion_repository.types import FaceEntry, FaceOrientation


# Standard orientation angles for legacy support
STANDARD_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]

# Default orientation tolerance in degrees
DEFAULT_TOLERANCE = 22


class OrientationMatcher:
    """Matches face orientations for optimal face selection."""
    
    @staticmethod
    def get_closest_standard_angle(angle: float) -> int:
        """
        Get closest standard orientation angle.
        
        Args:
            angle: Orientation angle in degrees (0-360)
            
        Returns:
            Closest standard angle (0, 45, 90, 135, 180, 225, 270, 315)
        """
        # Normalize angle to 0-360
        normalized = angle % 360
        
        # Find closest standard angle
        return min(STANDARD_ANGLES, key=lambda x: abs(x - normalized))
    
    @staticmethod
    def is_orientation_similar(
        angle1: int,
        angle2: int,
        tolerance: int = DEFAULT_TOLERANCE
    ) -> bool:
        """
        Check if two orientations are similar within tolerance.
        
        Args:
            angle1: First orientation angle
            angle2: Second orientation angle
            tolerance: Maximum angular difference (degrees)
            
        Returns:
            True if orientations are similar
        """
        # Calculate angular difference (handle wrap-around)
        diff = abs(angle1 - angle2)
        if diff > 180:
            diff = 360 - diff
        
        return diff <= tolerance
    
    @staticmethod
    def calculate_orientation_distance(
        orient1: FaceOrientation,
        orient2: FaceOrientation
    ) -> float:
        """
        Calculate angular distance between two 3D orientations.
        
        Uses weighted combination of yaw, pitch, and roll differences.
        
        Args:
            orient1: First orientation
            orient2: Second orientation
            
        Returns:
            Combined angular distance (weighted)
        """
        def normalize_angle(angle: float) -> float:
            """Normalize angle to -180 to 180 range."""
            return ((angle + 180) % 360) - 180
        
        yaw_diff = abs(normalize_angle(orient1.yaw - orient2.yaw))
        pitch_diff = abs(normalize_angle(orient1.pitch - orient2.pitch))
        roll_diff = abs(normalize_angle(orient1.roll - orient2.roll))
        
        # Weighted combination: yaw is most important
        weighted_distance = (yaw_diff * 1.0) + (pitch_diff * 0.5) + (roll_diff * 0.3)
        
        return weighted_distance
    
    @staticmethod
    def find_best_match(
        target_orientation: FaceOrientation,
        candidate_faces: List[FaceEntry]
    ) -> Optional[FaceEntry]:
        """
        Find best matching face for target orientation.
        
        Selects the face with the closest orientation and highest quality.
        
        Args:
            target_orientation: Target orientation to match
            candidate_faces: List of candidate faces
            
        Returns:
            Best matching face entry, or None if no candidates
        """
        if not candidate_faces:
            return None
        
        # Score each candidate (lower is better)
        scored_faces = []
        for face in candidate_faces:
            orientation_distance = OrientationMatcher.calculate_orientation_distance(
                target_orientation,
                face.orientation
            )
            
            # Combine orientation distance with quality (inverse)
            # Good quality reduces the score
            quality_factor = 1.0 - face.quality_metrics.overall_quality
            combined_score = orientation_distance + (quality_factor * 20)
            
            scored_faces.append((combined_score, face))
        
        # Return face with lowest score
        scored_faces.sort(key=lambda x: x[0])
        return scored_faces[0][1]
    
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
