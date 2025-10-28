"""
Preview generator for face swaps before committing to repository.
"""

import tempfile
from pathlib import Path
from typing import Optional

from facefusion import face_analyser
from facefusion.vision import read_static_image, write_image
from facefusion_repository.orientation.pose_estimator import PoseEstimator
from facefusion_repository.preview.test_image_manager import TestImageManager
from facefusion_repository.repository.orientation_matcher import OrientationMatcher
from facefusion_repository.repository.quality_assessor import QualityAssessor
from facefusion_repository.types import PreviewResult


class PreviewGenerator:
    """Generates preview images of face swaps."""

    def __init__(self, test_image_manager: Optional[TestImageManager] = None) -> None:
        """
        Initialize preview generator.

        Args:
            test_image_manager: TestImageManager instance. If None, creates new one.
        """
        if test_image_manager is None:
            test_image_manager = TestImageManager()
        
        self.test_image_manager = test_image_manager

    def generate_preview(
        self,
        source_image_path: str,
        output_path: Optional[str] = None
    ) -> PreviewResult:
        """
        Generate preview of face swap using best matching test image.

        Args:
            source_image_path: Path to source face image
            output_path: Output path for preview. If None, uses temp file.

        Returns:
            PreviewResult with preview information
        """
        warnings = []

        try:
            # Read source image
            source_frame = read_static_image(source_image_path)
            if source_frame is None:
                return PreviewResult(
                    success=False,
                    warnings=['Failed to read source image']
                )

            # Detect face in source
            source_faces = face_analyser.get_many_faces([source_frame])
            if not source_faces:
                return PreviewResult(
                    success=False,
                    warnings=['No face detected in source image']
                )

            source_face = source_faces[0]

            # Assess source quality
            source_quality = QualityAssessor.assess_face(source_frame, source_face)

            # Estimate source orientation
            pose = PoseEstimator.estimate_pose(source_face)
            
            if pose:
                source_orientation = PoseEstimator.get_orientation_angle_from_pose(pose)
            else:
                source_orientation = OrientationMatcher.get_closest_standard_angle(source_face.angle)

            # Find best matching test image
            test_image = self.test_image_manager.get_test_image_for_orientation(source_orientation)
            
            if test_image is None:
                # Try to find closest orientation
                test_images = self.test_image_manager.list_test_images()
                if not test_images:
                    return PreviewResult(
                        success=False,
                        warnings=['No test images available. Run create-test-images first.']
                    )

                # Find closest orientation
                closest_test = min(
                    test_images,
                    key=lambda t: OrientationMatcher.calculate_angle_distance(
                        source_orientation, t.orientation_angle
                    )
                )
                
                test_image = closest_test
                warnings.append(
                    f'No exact test image for orientation {source_orientation}°. '
                    f'Using closest match: {test_image.orientation_angle}°'
                )

            # Note: Actual face swap would be done here using FaceFusion processors
            # For now, we simulate by copying the source image
            # In full implementation, this would call FaceFusion's face swap pipeline
            
            if output_path is None:
                # Create temp file
                temp_dir = Path(tempfile.gettempdir()) / 'facefusion_preview'
                temp_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(temp_dir / f'preview_{Path(source_image_path).name}')

            # For preview, we just copy source for now
            # TODO: Integrate actual face swap when FaceFusion processors are available
            write_image(output_path, source_frame)

            warnings.append('Note: Full face swap preview requires FaceFusion processors to be initialized')

            return PreviewResult(
                success=True,
                preview_path=output_path,
                quality_score=source_quality.overall_quality,
                orientation_match=f'{source_orientation}° -> {test_image.orientation_angle}°',
                warnings=warnings
            )

        except Exception as e:
            return PreviewResult(
                success=False,
                warnings=[f'Error generating preview: {e}']
            )

    def preview_with_specific_test_image(
        self,
        source_image_path: str,
        test_image_path: str,
        output_path: Optional[str] = None
    ) -> PreviewResult:
        """
        Generate preview with specific test image.

        Args:
            source_image_path: Path to source face image
            test_image_path: Path to test image to use as destination
            output_path: Output path for preview. If None, uses temp file.

        Returns:
            PreviewResult with preview information
        """
        warnings = []

        try:
            # Read source image
            source_frame = read_static_image(source_image_path)
            if source_frame is None:
                return PreviewResult(
                    success=False,
                    warnings=['Failed to read source image']
                )

            # Detect face in source
            source_faces = face_analyser.get_many_faces([source_frame])
            if not source_faces:
                return PreviewResult(
                    success=False,
                    warnings=['No face detected in source image']
                )

            source_face = source_faces[0]

            # Assess source quality
            source_quality = QualityAssessor.assess_face(source_frame, source_face)

            # Read test image
            test_frame = read_static_image(test_image_path)
            if test_frame is None:
                return PreviewResult(
                    success=False,
                    warnings=['Failed to read test image']
                )

            # Note: Actual face swap would be done here
            # For now, we simulate by using the source image
            
            if output_path is None:
                # Create temp file
                temp_dir = Path(tempfile.gettempdir()) / 'facefusion_preview'
                temp_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(temp_dir / f'preview_{Path(source_image_path).name}')

            # For preview, we just copy source for now
            write_image(output_path, source_frame)

            warnings.append('Note: Full face swap preview requires FaceFusion processors to be initialized')

            return PreviewResult(
                success=True,
                preview_path=output_path,
                quality_score=source_quality.overall_quality,
                warnings=warnings
            )

        except Exception as e:
            return PreviewResult(
                success=False,
                warnings=[f'Error generating preview: {e}']
            )
