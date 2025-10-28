"""
Tests for FaceFusion Repository System - Orientation Matcher.
"""

import pytest

from facefusion_repository.repository.orientation_matcher import OrientationMatcher
from facefusion_repository.types import FaceEntry, FaceMetadata, QualityMetrics
import numpy


def create_test_face_entry(face_id: str, orientation: int, quality: float = 0.8) -> FaceEntry:
    """
    Create a test face entry.

    Args:
        face_id: Face identifier
        orientation: Orientation angle
        quality: Overall quality score

    Returns:
        Test FaceEntry object
    """
    return FaceEntry(
        id=face_id,
        file_path=f'/test/{face_id}.jpg',
        orientation_angle=orientation,
        quality_metrics=QualityMetrics(
            resolution=(512, 512),
            sharpness=0.7,
            detector_score=0.9,
            brightness=0.6,
            contrast=0.5,
            overall_quality=quality
        ),
        face_embedding=numpy.zeros(512),
        face_landmarks={'5': [], '68': []},
        metadata=FaceMetadata(
            added_date='2025-10-28T00:00:00Z',
            name=f'Test Face {face_id}',
            tags=['test']
        )
    )


def test_normalize_angle() -> None:
    """Test angle normalization."""
    assert OrientationMatcher.normalize_angle(0) == 0
    assert OrientationMatcher.normalize_angle(360) == 0
    assert OrientationMatcher.normalize_angle(720) == 0
    assert OrientationMatcher.normalize_angle(-90) == 270
    assert OrientationMatcher.normalize_angle(450) == 90


def test_get_closest_standard_angle() -> None:
    """Test mapping to closest standard angle."""
    assert OrientationMatcher.get_closest_standard_angle(0) == 0
    assert OrientationMatcher.get_closest_standard_angle(10) == 0
    assert OrientationMatcher.get_closest_standard_angle(22) == 0
    assert OrientationMatcher.get_closest_standard_angle(23) == 45
    assert OrientationMatcher.get_closest_standard_angle(45) == 45
    assert OrientationMatcher.get_closest_standard_angle(90) == 90
    assert OrientationMatcher.get_closest_standard_angle(135) == 135
    assert OrientationMatcher.get_closest_standard_angle(180) == 180
    assert OrientationMatcher.get_closest_standard_angle(270) == 270
    assert OrientationMatcher.get_closest_standard_angle(315) == 315
    assert OrientationMatcher.get_closest_standard_angle(350) == 0


def test_calculate_angle_distance() -> None:
    """Test angular distance calculation."""
    # Same angle
    assert OrientationMatcher.calculate_angle_distance(0, 0) == 0

    # Opposite angles
    assert OrientationMatcher.calculate_angle_distance(0, 180) == 180

    # Adjacent angles
    assert OrientationMatcher.calculate_angle_distance(0, 45) == 45
    assert OrientationMatcher.calculate_angle_distance(45, 0) == 45

    # Wrap-around cases
    assert OrientationMatcher.calculate_angle_distance(0, 350) == 10
    assert OrientationMatcher.calculate_angle_distance(350, 0) == 10
    assert OrientationMatcher.calculate_angle_distance(10, 350) == 20

    # Maximum distance should be 180
    assert OrientationMatcher.calculate_angle_distance(0, 180) <= 180
    assert OrientationMatcher.calculate_angle_distance(90, 270) <= 180


def test_find_best_match() -> None:
    """Test finding best matching face."""
    # Create test faces at different orientations
    faces = [
        create_test_face_entry('face1', 0, 0.9),
        create_test_face_entry('face2', 45, 0.8),
        create_test_face_entry('face3', 90, 0.7),
    ]

    # Test exact match
    match = OrientationMatcher.find_best_match(0, faces, max_angle_diff=45)
    assert match is not None
    assert match.id == 'face1'

    # Test close match
    match = OrientationMatcher.find_best_match(10, faces, max_angle_diff=45)
    assert match is not None
    assert match.id == 'face1'

    # Test no match (too far)
    match = OrientationMatcher.find_best_match(180, faces, max_angle_diff=45)
    assert match is None

    # Test empty list
    match = OrientationMatcher.find_best_match(0, [], max_angle_diff=45)
    assert match is None


def test_is_orientation_similar() -> None:
    """Test orientation similarity checking."""
    # Similar orientations
    assert OrientationMatcher.is_orientation_similar(0, 10, threshold=15)
    assert OrientationMatcher.is_orientation_similar(45, 50, threshold=15)

    # Not similar
    assert not OrientationMatcher.is_orientation_similar(0, 45, threshold=15)
    assert not OrientationMatcher.is_orientation_similar(0, 30, threshold=15)

    # Wrap-around cases
    assert OrientationMatcher.is_orientation_similar(0, 350, threshold=15)
    assert OrientationMatcher.is_orientation_similar(350, 0, threshold=15)


def test_group_by_orientation() -> None:
    """Test grouping faces by orientation."""
    faces = [
        create_test_face_entry('face1', 0),
        create_test_face_entry('face2', 5),    # Should group with 0°
        create_test_face_entry('face3', 45),
        create_test_face_entry('face4', 50),   # Should group with 45°
        create_test_face_entry('face5', 90),
        create_test_face_entry('face6', 180),
    ]

    groups = OrientationMatcher.group_by_orientation(faces, tolerance=45)

    # Check that groups exist for standard angles
    assert 0 in groups
    assert 45 in groups
    assert 90 in groups
    assert 180 in groups

    # Check specific groupings
    assert len(groups[0]) == 2  # face1, face2
    assert len(groups[45]) == 2  # face3, face4
    assert len(groups[90]) == 1  # face5
    assert len(groups[180]) == 1  # face6

    # Check empty groups
    assert len(groups[135]) == 0
    assert len(groups[225]) == 0
    assert len(groups[270]) == 0
    assert len(groups[315]) == 0


def test_get_best_quality_face() -> None:
    """Test selecting highest quality face."""
    faces = [
        create_test_face_entry('face1', 0, 0.5),
        create_test_face_entry('face2', 0, 0.9),  # Best quality
        create_test_face_entry('face3', 0, 0.7),
    ]

    best = OrientationMatcher.get_best_quality_face(faces)
    assert best is not None
    assert best.id == 'face2'
    assert best.quality_metrics.overall_quality == 0.9

    # Test with empty list
    best = OrientationMatcher.get_best_quality_face([])
    assert best is None

    # Test with single face
    best = OrientationMatcher.get_best_quality_face([faces[0]])
    assert best is not None
    assert best.id == 'face1'
