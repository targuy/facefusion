"""
FaceFusion Repository System.

A comprehensive face management system with multi-axis orientation detection,
character-based organization, and automated face selection for optimal swapping.
"""

__version__ = '2.0.0'

from facefusion_repository.types import (
    FaceOrientation,
    FaceEntry,
    FaceMetadata,
    Character,
    QualityMetrics,
    QualityThresholds,
    DEFAULT_QUALITY_THRESHOLDS
)

__all__ = [
    'FaceOrientation',
    'FaceEntry',
    'FaceMetadata',
    'Character',
    'QualityMetrics',
    'QualityThresholds',
    'DEFAULT_QUALITY_THRESHOLDS'
]
