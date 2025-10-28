"""
Quality assessment for face images in the repository.
"""

from typing import Tuple

import cv2
import numpy

from facefusion.types import BoundingBox, Face, VisionFrame
from facefusion_repository.types import QualityMetrics, QualityThresholds


class QualityAssessor:
    """Assesses face image quality based on multiple metrics."""

    @staticmethod
    def assess_face(vision_frame: VisionFrame, face: Face) -> QualityMetrics:
        """
        Calculate quality metrics for a detected face.

        Args:
            vision_frame: The image containing the face
            face: The detected face object

        Returns:
            QualityMetrics object with all quality measurements
        """
        bounding_box = face.bounding_box
        resolution = (
            int(bounding_box[2] - bounding_box[0]),
            int(bounding_box[3] - bounding_box[1])
        )

        sharpness = QualityAssessor.calculate_sharpness(vision_frame, bounding_box)
        brightness = QualityAssessor.calculate_brightness(vision_frame, bounding_box)
        contrast = QualityAssessor.calculate_contrast(vision_frame, bounding_box)
        detector_score = face.score_set['detector']

        # Calculate overall quality as weighted average
        overall_quality = (
            sharpness * 0.3 +
            detector_score * 0.3 +
            contrast * 0.2 +
            min(1.0, max(0.0, (brightness - 0.2) / 0.7)) * 0.2
        )

        return QualityMetrics(
            resolution=resolution,
            sharpness=float(sharpness),
            detector_score=float(detector_score),
            brightness=float(brightness),
            contrast=float(contrast),
            overall_quality=float(overall_quality)
        )

    @staticmethod
    def calculate_sharpness(vision_frame: VisionFrame, bounding_box: BoundingBox) -> float:
        """
        Calculate Laplacian variance as sharpness metric.

        Args:
            vision_frame: The image containing the face
            bounding_box: Face bounding box coordinates

        Returns:
            Normalized sharpness score (0.0 to 1.0)
        """
        x1, y1, x2, y2 = map(int, bounding_box)
        face_region = vision_frame[y1:y2, x1:x2]

        if face_region.size == 0:
            return 0.0

        # Convert to grayscale if needed
        if len(face_region.shape) == 3:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_region

        # Calculate Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = numpy.var(laplacian)

        # Normalize to 0-1 range (empirically, values above 100 are sharp)
        normalized = min(1.0, variance / 100.0)

        return float(normalized)

    @staticmethod
    def calculate_brightness(vision_frame: VisionFrame, bounding_box: BoundingBox) -> float:
        """
        Calculate average brightness in face region.

        Args:
            vision_frame: The image containing the face
            bounding_box: Face bounding box coordinates

        Returns:
            Brightness value (0.0 to 1.0)
        """
        x1, y1, x2, y2 = map(int, bounding_box)
        face_region = vision_frame[y1:y2, x1:x2]

        if face_region.size == 0:
            return 0.0

        # Convert to grayscale if needed
        if len(face_region.shape) == 3:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_region

        # Calculate mean brightness
        brightness = numpy.mean(gray) / 255.0

        return float(brightness)

    @staticmethod
    def calculate_contrast(vision_frame: VisionFrame, bounding_box: BoundingBox) -> float:
        """
        Calculate standard deviation as contrast metric.

        Args:
            vision_frame: The image containing the face
            bounding_box: Face bounding box coordinates

        Returns:
            Normalized contrast value (0.0 to 1.0)
        """
        x1, y1, x2, y2 = map(int, bounding_box)
        face_region = vision_frame[y1:y2, x1:x2]

        if face_region.size == 0:
            return 0.0

        # Convert to grayscale if needed
        if len(face_region.shape) == 3:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_region

        # Calculate standard deviation as contrast
        contrast = numpy.std(gray) / 128.0  # Normalize to 0-1 range

        return float(min(1.0, contrast))

    @staticmethod
    def is_acceptable_quality(metrics: QualityMetrics, thresholds: QualityThresholds) -> bool:
        """
        Check if quality metrics meet minimum thresholds.

        Args:
            metrics: Quality metrics to check
            thresholds: Minimum acceptable thresholds

        Returns:
            True if all quality checks pass
        """
        if metrics.resolution[0] < thresholds.min_resolution[0]:
            return False
        if metrics.resolution[1] < thresholds.min_resolution[1]:
            return False
        if metrics.sharpness < thresholds.min_sharpness:
            return False
        if metrics.detector_score < thresholds.min_detector_score:
            return False
        if metrics.brightness < thresholds.min_brightness:
            return False
        if metrics.brightness > thresholds.max_brightness:
            return False
        if metrics.contrast < thresholds.min_contrast:
            return False
        if metrics.overall_quality < thresholds.min_overall_quality:
            return False

        return True
