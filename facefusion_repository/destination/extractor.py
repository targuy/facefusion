"""
Face extraction from destination media.

Handles detection and extraction of faces from images and video frames,
with quality filtering and batch processing support.
"""

from typing import List, Optional
import numpy as np

from facefusion import face_analyser
from facefusion.types import Face, VisionFrame
from facefusion.vision import read_static_image
from facefusion_repository.repository.quality_assessor import QualityAssessor
from facefusion_repository.types import (
    DEFAULT_QUALITY_THRESHOLDS,
    QualityMetrics,
    QualityThresholds
)


class FaceExtractor:
    """Extracts faces from images and video frames."""

    @staticmethod
    def extract_from_image(
        image_path: str,
        quality_thresholds: Optional[QualityThresholds] = None
    ) -> List[Face]:
        """
        Extract faces from an image file.

        Args:
            image_path: Path to image file
            quality_thresholds: Optional quality thresholds for filtering

        Returns:
            List of detected Face objects that meet quality thresholds
        """
        if quality_thresholds is None:
            quality_thresholds = DEFAULT_QUALITY_THRESHOLDS

        # Read image
        vision_frame = read_static_image(image_path)
        if vision_frame is None:
            return []

        # Detect faces
        faces = face_analyser.get_many_faces([vision_frame])
        if not faces:
            return []

        # Filter by quality
        filtered_faces = []
        for face in faces:
            quality_metrics = QualityAssessor.assess_face(vision_frame, face)
            if QualityAssessor.is_acceptable_quality(quality_metrics, quality_thresholds):
                filtered_faces.append(face)

        return filtered_faces

    @staticmethod
    def extract_from_frame(
        vision_frame: VisionFrame,
        quality_thresholds: Optional[QualityThresholds] = None
    ) -> List[Face]:
        """
        Extract faces from a video frame.

        Args:
            vision_frame: Video frame as numpy array
            quality_thresholds: Optional quality thresholds for filtering

        Returns:
            List of detected Face objects that meet quality thresholds
        """
        if quality_thresholds is None:
            quality_thresholds = DEFAULT_QUALITY_THRESHOLDS

        if vision_frame is None:
            return []

        # Detect faces
        faces = face_analyser.get_many_faces([vision_frame])
        if not faces:
            return []

        # Filter by quality
        filtered_faces = []
        for face in faces:
            quality_metrics = QualityAssessor.assess_face(vision_frame, face)
            if QualityAssessor.is_acceptable_quality(quality_metrics, quality_thresholds):
                filtered_faces.append(face)

        return filtered_faces

    @staticmethod
    def get_face_quality(vision_frame: VisionFrame, face: Face) -> QualityMetrics:
        """
        Get quality metrics for a face.

        Args:
            vision_frame: Frame containing the face
            face: Face object

        Returns:
            QualityMetrics object
        """
        return QualityAssessor.assess_face(vision_frame, face)

    @staticmethod
    def is_quality_acceptable(
        quality_metrics: QualityMetrics,
        quality_thresholds: Optional[QualityThresholds] = None
    ) -> bool:
        """
        Check if face quality meets thresholds.

        Args:
            quality_metrics: Quality metrics to check
            quality_thresholds: Optional quality thresholds

        Returns:
            True if quality is acceptable
        """
        if quality_thresholds is None:
            quality_thresholds = DEFAULT_QUALITY_THRESHOLDS

        return QualityAssessor.is_acceptable_quality(quality_metrics, quality_thresholds)
