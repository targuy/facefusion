"""
Quality assessment for face images.

Evaluates face quality based on multiple metrics including sharpness,
brightness, contrast, and detector confidence.
"""

import cv2
import numpy as np
from typing import Tuple

from facefusion_repository.types import QualityMetrics, QualityThresholds, DEFAULT_QUALITY_THRESHOLDS


class QualityAssessor:
    """Assesses face image quality using multiple metrics."""
    
    @staticmethod
    def assess_quality(
        image_path: str,
        face_detector_score: float,
        thresholds: QualityThresholds = DEFAULT_QUALITY_THRESHOLDS
    ) -> Tuple[QualityMetrics, bool]:
        """
        Assess quality of a face image.
        
        Args:
            image_path: Path to the face image
            face_detector_score: Confidence score from face detector
            thresholds: Quality thresholds to validate against
            
        Returns:
            Tuple of (QualityMetrics, passes_threshold)
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Calculate metrics
        resolution = (image.shape[1], image.shape[0])
        sharpness = QualityAssessor._calculate_sharpness(image)
        brightness = QualityAssessor._calculate_brightness(image)
        contrast = QualityAssessor._calculate_contrast(image)
        
        # Calculate overall quality (weighted average)
        overall_quality = (
            0.35 * min(sharpness / 100.0, 1.0) +
            0.25 * brightness +
            0.20 * contrast +
            0.20 * face_detector_score
        )
        
        metrics = QualityMetrics(
            resolution=resolution,
            sharpness=sharpness,
            detector_score=face_detector_score,
            brightness=brightness,
            contrast=contrast,
            overall_quality=overall_quality
        )
        
        # Check if passes thresholds
        passes = QualityAssessor._check_thresholds(metrics, thresholds)
        
        return metrics, passes
    
    @staticmethod
    def _calculate_sharpness(image: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return float(variance)
    
    @staticmethod
    def _calculate_brightness(image: np.ndarray) -> float:
        """Calculate normalized brightness (0.0 to 1.0)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = gray.mean() / 255.0
        return float(mean_brightness)
    
    @staticmethod
    def _calculate_contrast(image: np.ndarray) -> float:
        """Calculate contrast using standard deviation."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        std_dev = gray.std() / 255.0
        return float(std_dev)
    
    @staticmethod
    def _check_thresholds(
        metrics: QualityMetrics,
        thresholds: QualityThresholds
    ) -> bool:
        """Check if metrics meet quality thresholds."""
        return (
            metrics.resolution[0] >= thresholds.min_resolution[0] and
            metrics.resolution[1] >= thresholds.min_resolution[1] and
            metrics.sharpness >= thresholds.min_sharpness and
            metrics.detector_score >= thresholds.min_detector_score and
            metrics.brightness >= thresholds.min_brightness and
            metrics.brightness <= thresholds.max_brightness and
            metrics.contrast >= thresholds.min_contrast and
            metrics.overall_quality >= thresholds.min_overall_quality
        )
