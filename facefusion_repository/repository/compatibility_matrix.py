"""
Compatibility matrix for face swap operations.
"""

from typing import Dict, List

from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.repository.orientation_matcher import OrientationMatcher
from facefusion_repository.types import CoverageReport, FaceEntry


class CompatibilityMatrix:
    """Manages face swap compatibility matrix based on orientations."""

    def __init__(self, repository_manager: RepositoryManager) -> None:
        """
        Initialize compatibility matrix.

        Args:
            repository_manager: Repository manager instance
        """
        self.repository_manager = repository_manager

    def build_matrix(self) -> Dict[int, List[str]]:
        """
        Build orientation to face IDs mapping.

        Returns:
            Dictionary mapping orientation angles to lists of face IDs
        """
        matrix: Dict[int, List[str]] = {}

        faces = self.repository_manager.list_faces()

        for face in faces:
            angle = face.orientation_angle
            if angle not in matrix:
                matrix[angle] = []
            matrix[angle].append(face.id)

        return matrix

    def get_available_orientations(self) -> List[int]:
        """
        Get list of all available orientations in repository.

        Returns:
            Sorted list of orientation angles
        """
        faces = self.repository_manager.list_faces()
        orientations = set(face.orientation_angle for face in faces)
        return sorted(orientations)

    def get_faces_for_orientation(
        self,
        orientation: int,
        tolerance: int = 45
    ) -> List[FaceEntry]:
        """
        Get all faces within tolerance of given orientation.

        Args:
            orientation: Target orientation angle
            tolerance: Angular tolerance in degrees

        Returns:
            List of matching face entries
        """
        faces = self.repository_manager.list_faces()

        matching_faces = [
            face for face in faces
            if OrientationMatcher.calculate_angle_distance(
                face.orientation_angle, orientation
            ) <= tolerance
        ]

        # Sort by quality
        matching_faces.sort(
            key=lambda f: f.quality_metrics.overall_quality,
            reverse=True
        )

        return matching_faces

    def visualize_matrix(self) -> str:
        """
        Generate ASCII visualization of compatibility matrix.

        Returns:
            String representation of the matrix
        """
        matrix = self.build_matrix()

        if not matrix:
            return 'Repository is empty - no faces available.'

        lines = []
        lines.append('Face Repository Compatibility Matrix')
        lines.append('=' * 60)
        lines.append('')

        # Get statistics
        stats = self.repository_manager.get_statistics()
        if stats:
            lines.append(f'Total Faces: {stats.total_faces}')
            lines.append(f'Average Quality: {stats.average_quality:.2f}')
            lines.append(f'Storage Size: {stats.total_size_mb:.2f} MB')
            lines.append('')

        # Show orientation coverage
        lines.append('Orientation Coverage:')
        lines.append('-' * 60)

        for angle in OrientationMatcher.STANDARD_ANGLES:
            face_count = len(matrix.get(angle, []))
            bar_length = min(40, face_count * 5)
            bar = '█' * bar_length

            if face_count > 0:
                # Get faces for this orientation
                faces = [
                    face for face in self.repository_manager.list_faces()
                    if face.orientation_angle == angle
                ]
                best_quality = max(f.quality_metrics.overall_quality for f in faces) if faces else 0.0

                lines.append(f'{angle:3d}° | {bar} {face_count} face(s) (Q: {best_quality:.2f})')
            else:
                lines.append(f'{angle:3d}° | (no faces)')

        lines.append('')

        # Show face details
        if matrix:
            lines.append('Face Details:')
            lines.append('-' * 60)

            for angle in sorted(matrix.keys()):
                lines.append(f'\nOrientation {angle}°:')
                for face_id in matrix[angle]:
                    face = self.repository_manager.get_face(face_id)
                    if face:
                        name = face.metadata.name or 'Unnamed'
                        quality = face.quality_metrics.overall_quality
                        lines.append(f'  - {face_id}: {name} (Quality: {quality:.2f})')

        return '\n'.join(lines)

    def get_coverage_report(self) -> CoverageReport:
        """
        Generate report on orientation coverage.

        Returns:
            CoverageReport object
        """
        matrix = self.build_matrix()

        covered_orientations = sorted(matrix.keys())
        all_standard = set(OrientationMatcher.STANDARD_ANGLES)
        covered_set = set(covered_orientations)
        missing_orientations = sorted(all_standard - covered_set)

        total_orientations = len(OrientationMatcher.STANDARD_ANGLES)
        covered_count = len(covered_set & all_standard)
        coverage_percentage = (covered_count / total_orientations) * 100

        faces_per_orientation = {
            angle: len(matrix.get(angle, []))
            for angle in OrientationMatcher.STANDARD_ANGLES
        }

        return CoverageReport(
            total_orientations=total_orientations,
            covered_orientations=covered_orientations,
            missing_orientations=missing_orientations,
            coverage_percentage=coverage_percentage,
            faces_per_orientation=faces_per_orientation
        )
