"""
Test image management for preview system.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from facefusion import face_analyser
from facefusion.vision import read_static_image
from facefusion_repository.orientation.pose_estimator import PoseEstimator
from facefusion_repository.repository.quality_assessor import QualityAssessor
from facefusion_repository.types import TestImage


class TestImageManager:
    """Manages test images for preview testing."""

    def __init__(self, test_images_dir: Optional[str] = None) -> None:
        """
        Initialize test image manager.

        Args:
            test_images_dir: Path to test images directory. If None, uses default.
        """
        if test_images_dir is None:
            repo_path = Path.home() / '.facefusion_repository'
            test_images_dir = str(repo_path / 'test_images')
        
        self.test_images_dir = Path(test_images_dir)
        self.metadata_file = self.test_images_dir / 'test_images.json'
        
        self._test_images: Dict[int, TestImage] = {}
        self._loaded = False

    def _load_metadata(self) -> bool:
        """
        Load test image metadata from file.

        Returns:
            True if load successful
        """
        if self._loaded:
            return True

        if not self.metadata_file.exists():
            return False

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._test_images = {}
            for item in data.get('test_images', []):
                test_image = TestImage(
                    path=item['path'],
                    orientation_angle=item['orientation_angle'],
                    face_count=item['face_count'],
                    best_face_quality=item['best_face_quality']
                )
                self._test_images[test_image.orientation_angle] = test_image

            self._loaded = True
            return True
        except Exception as e:
            print(f'Error loading test image metadata: {e}')
            return False

    def _save_metadata(self) -> bool:
        """
        Save test image metadata to file.

        Returns:
            True if save successful
        """
        try:
            # Create directory if needed
            self.test_images_dir.mkdir(parents=True, exist_ok=True)

            data = {
                'test_images': [
                    {
                        'path': img.path,
                        'orientation_angle': img.orientation_angle,
                        'face_count': img.face_count,
                        'best_face_quality': img.best_face_quality
                    }
                    for img in self._test_images.values()
                ]
            }

            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f'Error saving test image metadata: {e}')
            return False

    def create_test_images_from_directory(
        self,
        source_dir: str,
        output_dir: Optional[str] = None
    ) -> int:
        """
        Create test image collection from source directory.
        Automatically selects the best face image for each orientation.

        Args:
            source_dir: Directory containing source images
            output_dir: Output directory for test images. If None, uses default.

        Returns:
            Number of test images created
        """
        if output_dir is None:
            output_dir = str(self.test_images_dir)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        source_path = Path(source_dir)
        
        if not source_path.exists():
            print(f'Source directory does not exist: {source_dir}')
            return 0

        # Group images by orientation
        orientation_candidates: Dict[int, List[tuple]] = {}  # orientation -> [(quality, path, face)]

        # Scan all images in source directory
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        image_files = [
            f for f in source_path.rglob('*')
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        print(f'Scanning {len(image_files)} images...')

        for image_file in image_files:
            try:
                # Read image
                vision_frame = read_static_image(str(image_file))
                if vision_frame is None:
                    continue

                # Detect faces
                faces = face_analyser.get_many_faces([vision_frame])
                if not faces:
                    continue

                # Process each face
                for face in faces:
                    # Assess quality
                    quality_metrics = QualityAssessor.assess_face(vision_frame, face)
                    
                    # Estimate pose to get orientation
                    pose = PoseEstimator.estimate_pose(face)
                    
                    if pose:
                        orientation_angle = PoseEstimator.get_orientation_angle_from_pose(pose)
                    else:
                        # Fallback to basic angle
                        from facefusion_repository.repository.orientation_matcher import OrientationMatcher
                        orientation_angle = OrientationMatcher.get_closest_standard_angle(face.angle)

                    # Add to candidates
                    if orientation_angle not in orientation_candidates:
                        orientation_candidates[orientation_angle] = []
                    
                    orientation_candidates[orientation_angle].append(
                        (quality_metrics.overall_quality, str(image_file), len(faces))
                    )

            except Exception as e:
                print(f'Warning: Could not process {image_file}: {e}')
                continue

        # Select best image for each orientation
        count = 0
        self._test_images = {}

        for orientation, candidates in orientation_candidates.items():
            if not candidates:
                continue

            # Sort by quality (descending)
            candidates.sort(key=lambda x: x[0], reverse=True)
            
            # Take the best one
            best_quality, best_path, face_count = candidates[0]
            
            # Copy to test images directory
            dest_filename = f'test_orientation_{orientation:03d}{Path(best_path).suffix}'
            dest_path = output_path / dest_filename
            
            shutil.copy2(best_path, dest_path)
            
            # Create test image entry
            test_image = TestImage(
                path=str(dest_path),
                orientation_angle=orientation,
                face_count=face_count,
                best_face_quality=best_quality
            )
            
            self._test_images[orientation] = test_image
            count += 1
            
            print(f'✓ Created test image for orientation {orientation}° (quality: {best_quality:.2f})')

        # Save metadata
        self._save_metadata()
        
        print(f'\nCreated {count} test images covering {count} orientations')
        return count

    def get_test_image_for_orientation(self, orientation: int) -> Optional[TestImage]:
        """
        Get test image for specific orientation.

        Args:
            orientation: Orientation angle

        Returns:
            TestImage object or None
        """
        self._load_metadata()
        return self._test_images.get(orientation)

    def list_test_images(self) -> List[TestImage]:
        """
        List all test images.

        Returns:
            List of TestImage objects
        """
        self._load_metadata()
        return list(self._test_images.values())

    def get_coverage(self) -> Dict[str, any]:
        """
        Get test image coverage statistics.

        Returns:
            Dictionary with coverage information
        """
        self._load_metadata()
        
        standard_angles = [0, 45, 90, 135, 180, 225, 270, 315]
        covered_angles = [angle for angle in standard_angles if angle in self._test_images]
        missing_angles = [angle for angle in standard_angles if angle not in self._test_images]
        
        return {
            'total_test_images': len(self._test_images),
            'covered_angles': covered_angles,
            'missing_angles': missing_angles,
            'coverage_percentage': (len(covered_angles) / len(standard_angles)) * 100
        }
