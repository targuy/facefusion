"""
Tests for FaceFusion Repository System - Quality Assessor.
"""

import numpy
import pytest

from facefusion.types import BoundingBox, Face, FaceLandmarkSet, FaceScoreSet
from facefusion_repository.repository.quality_assessor import QualityAssessor
from facefusion_repository.types import DEFAULT_QUALITY_THRESHOLDS


def create_test_face(detector_score: float = 0.9) -> Face:
    """
    Create a test face object.

    Args:
        detector_score: Face detection confidence score

    Returns:
        Test Face object
    """
    return Face(
        bounding_box=numpy.array([100, 100, 300, 300]),
        score_set=FaceScoreSet(
            detector=detector_score,
            landmarker=0.8
        ),
        landmark_set=FaceLandmarkSet(
            **{
                '5': numpy.zeros((5, 2)),
                '5/68': numpy.zeros((5, 2)),
                '68': numpy.zeros((68, 2)),
                '68/5': numpy.zeros((68, 2))
            }
        ),
        angle=0,
        embedding=numpy.zeros(512),
        embedding_norm=numpy.zeros(512),
        gender='female',
        age=range(25, 35),
        race='white'
    )


def create_test_frame(size: tuple = (400, 400, 3)) -> numpy.ndarray:
    """
    Create a test vision frame.

    Args:
        size: Frame dimensions (height, width, channels)

    Returns:
        Test vision frame
    """
    # Create a frame with some texture
    frame = numpy.random.randint(0, 255, size, dtype=numpy.uint8)
    return frame


def test_assess_face() -> None:
    """Test basic face quality assessment."""
    face = create_test_face()
    frame = create_test_frame()

    metrics = QualityAssessor.assess_face(frame, face)

    assert metrics is not None
    assert metrics.resolution == (200, 200)
    assert 0.0 <= metrics.sharpness <= 1.0
    assert 0.0 <= metrics.brightness <= 1.0
    assert 0.0 <= metrics.contrast <= 1.0
    assert 0.0 <= metrics.overall_quality <= 1.0
    assert metrics.detector_score == 0.9


def test_calculate_sharpness() -> None:
    """Test sharpness calculation."""
    # Create a sharp frame (high-frequency content)
    sharp_frame = numpy.random.randint(0, 255, (400, 400, 3), dtype=numpy.uint8)

    # Create a blurry frame (low-frequency content)
    blurry_frame = numpy.ones((400, 400, 3), dtype=numpy.uint8) * 128

    bounding_box = numpy.array([100, 100, 300, 300])

    sharp_score = QualityAssessor.calculate_sharpness(sharp_frame, bounding_box)
    blurry_score = QualityAssessor.calculate_sharpness(blurry_frame, bounding_box)

    # Sharp frame should have higher sharpness
    assert sharp_score > blurry_score
    assert 0.0 <= sharp_score <= 1.0
    assert 0.0 <= blurry_score <= 1.0


def test_calculate_brightness() -> None:
    """Test brightness calculation."""
    # Create a bright frame
    bright_frame = numpy.ones((400, 400, 3), dtype=numpy.uint8) * 200

    # Create a dark frame
    dark_frame = numpy.ones((400, 400, 3), dtype=numpy.uint8) * 50

    bounding_box = numpy.array([100, 100, 300, 300])

    bright_score = QualityAssessor.calculate_brightness(bright_frame, bounding_box)
    dark_score = QualityAssessor.calculate_brightness(dark_frame, bounding_box)

    # Bright frame should have higher brightness
    assert bright_score > dark_score
    assert 0.0 <= bright_score <= 1.0
    assert 0.0 <= dark_score <= 1.0


def test_calculate_contrast() -> None:
    """Test contrast calculation."""
    # Create a high-contrast frame
    high_contrast = numpy.zeros((400, 400, 3), dtype=numpy.uint8)
    high_contrast[0:200, :, :] = 255  # Half white, half black

    # Create a low-contrast frame
    low_contrast = numpy.ones((400, 400, 3), dtype=numpy.uint8) * 128

    bounding_box = numpy.array([100, 100, 300, 300])

    high_score = QualityAssessor.calculate_contrast(high_contrast, bounding_box)
    low_score = QualityAssessor.calculate_contrast(low_contrast, bounding_box)

    # High contrast frame should have higher score
    assert high_score > low_score
    assert 0.0 <= high_score <= 1.0
    assert 0.0 <= low_score <= 1.0


def test_is_acceptable_quality() -> None:
    """Test quality threshold checking."""
    face = create_test_face(detector_score=0.9)
    frame = create_test_frame()

    metrics = QualityAssessor.assess_face(frame, face)

    # With default thresholds
    result = QualityAssessor.is_acceptable_quality(metrics, DEFAULT_QUALITY_THRESHOLDS)
    assert isinstance(result, bool)


def test_empty_bounding_box() -> None:
    """Test handling of empty/invalid bounding box."""
    frame = create_test_frame()
    empty_bbox = numpy.array([100, 100, 100, 100])  # Zero-size bbox

    sharpness = QualityAssessor.calculate_sharpness(frame, empty_bbox)
    brightness = QualityAssessor.calculate_brightness(frame, empty_bbox)
    contrast = QualityAssessor.calculate_contrast(frame, empty_bbox)

    # Should return 0.0 for empty regions
    assert sharpness == 0.0
    assert brightness == 0.0
    assert contrast == 0.0
