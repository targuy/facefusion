"""
Tests for FaceFusion Repository System - Repository Matcher.
"""

import numpy as np
import pytest
from unittest.mock import Mock, patch

from facefusion.types import Face
from facefusion_repository.destination.matcher import FaceMatch, RepositoryMatcher
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.types import FaceEntry, FaceMetadata, QualityMetrics


def create_test_face_entry(face_id: str, orientation: int, quality: float = 0.8) -> FaceEntry:
    """Create a test face entry."""
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
        face_embedding=np.zeros(512),
        face_landmarks={'5': [], '68': []},
        metadata=FaceMetadata(
            added_date='2025-10-28T00:00:00Z',
            name=f'Test Face {face_id}',
            tags=['test']
        )
    )


def create_mock_face(angle: float = 0.0) -> Face:
    """Create a mock Face object."""
    face = Mock(spec=Face)
    face.angle = angle
    face.score_set = {'detector': 0.9}
    face.bounding_box = [100, 100, 200, 200]
    face.embedding = np.random.rand(512)
    return face


def test_face_match_creation():
    """Test FaceMatch object creation."""
    dest_face = create_mock_face(angle=10.0)
    repo_face = create_test_face_entry('face1', 0)
    
    match = FaceMatch(
        destination_face=dest_face,
        repository_face=repo_face,
        confidence=0.85,
        orientation_difference=10
    )
    
    assert match.destination_face == dest_face
    assert match.repository_face == repo_face
    assert match.confidence == 0.85
    assert match.orientation_difference == 10


def test_find_best_match_with_similar_orientation():
    """Test finding best match with similar orientation."""
    mock_repo_manager = Mock(spec=RepositoryManager)
    
    # Create repository faces at different orientations
    repo_faces = [
        create_test_face_entry('face1', 0, quality=0.9),
        create_test_face_entry('face2', 45, quality=0.8),
        create_test_face_entry('face3', 90, quality=0.7)
    ]
    mock_repo_manager.list_faces.return_value = repo_faces
    
    matcher = RepositoryMatcher(mock_repo_manager)
    
    # Test face at angle 5 (should match face1 at 0)
    dest_face = create_mock_face(angle=5.0)
    dest_quality = QualityMetrics((512, 512), 0.7, 0.9, 0.6, 0.5, 0.75)
    
    match = matcher.find_best_match(dest_face, dest_quality)
    
    assert match is not None
    assert match.repository_face.id == 'face1'
    assert match.orientation_difference <= 22


def test_find_best_match_no_repository_faces():
    """Test finding match when repository is empty."""
    mock_repo_manager = Mock(spec=RepositoryManager)
    mock_repo_manager.list_faces.return_value = []
    
    matcher = RepositoryMatcher(mock_repo_manager)
    
    dest_face = create_mock_face()
    dest_quality = QualityMetrics((512, 512), 0.7, 0.9, 0.6, 0.5, 0.75)
    
    match = matcher.find_best_match(dest_face, dest_quality)
    
    assert match is None


def test_find_best_match_no_similar_orientation():
    """Test finding match when no faces have similar orientation."""
    mock_repo_manager = Mock(spec=RepositoryManager)
    
    # Only have face at 180 degrees
    repo_faces = [create_test_face_entry('face1', 180, quality=0.9)]
    mock_repo_manager.list_faces.return_value = repo_faces
    
    matcher = RepositoryMatcher(mock_repo_manager)
    
    # Test face at 0 degrees (too far from 180)
    dest_face = create_mock_face(angle=0.0)
    dest_quality = QualityMetrics((512, 512), 0.7, 0.9, 0.6, 0.5, 0.75)
    
    match = matcher.find_best_match(dest_face, dest_quality, orientation_tolerance=22)
    
    # Should not match as difference is 180 degrees
    assert match is None


def test_find_all_matches():
    """Test finding matches for multiple destination faces."""
    mock_repo_manager = Mock(spec=RepositoryManager)
    
    repo_faces = [
        create_test_face_entry('face1', 0, quality=0.9),
        create_test_face_entry('face2', 90, quality=0.8)
    ]
    mock_repo_manager.list_faces.return_value = repo_faces
    
    matcher = RepositoryMatcher(mock_repo_manager)
    
    # Create destination faces
    dest_faces_with_quality = [
        (create_mock_face(angle=5.0), QualityMetrics((512, 512), 0.7, 0.9, 0.6, 0.5, 0.75)),
        (create_mock_face(angle=95.0), QualityMetrics((512, 512), 0.7, 0.8, 0.6, 0.5, 0.70)),
        (create_mock_face(angle=180.0), QualityMetrics((512, 512), 0.6, 0.7, 0.5, 0.4, 0.60))
    ]
    
    matches = matcher.find_all_matches(
        dest_faces_with_quality,
        orientation_tolerance=22,
        min_confidence=0.5
    )
    
    # Should match first two faces (0° and 90°), not 180°
    assert len(matches) == 2
    assert matches[0].repository_face.id == 'face1'
    assert matches[1].repository_face.id == 'face2'


def test_find_all_matches_min_confidence_filter():
    """Test that matches below min_confidence are filtered out."""
    mock_repo_manager = Mock(spec=RepositoryManager)
    
    # Create a repository face
    repo_faces = [create_test_face_entry('face1', 0, quality=0.5)]
    mock_repo_manager.list_faces.return_value = repo_faces
    
    matcher = RepositoryMatcher(mock_repo_manager)
    
    # Create destination face with low quality
    dest_faces_with_quality = [
        (create_mock_face(angle=0.0), QualityMetrics((256, 256), 0.3, 0.5, 0.5, 0.3, 0.40))
    ]
    
    # With high min_confidence, should filter out low-quality matches
    matches = matcher.find_all_matches(
        dest_faces_with_quality,
        min_confidence=0.8
    )
    
    assert len(matches) == 0


def test_get_match_statistics_empty():
    """Test statistics with no matches."""
    mock_repo_manager = Mock(spec=RepositoryManager)
    matcher = RepositoryMatcher(mock_repo_manager)
    
    stats = matcher.get_match_statistics([])
    
    assert stats['total_matches'] == 0
    assert stats['average_confidence'] == 0.0
    assert stats['matches_by_face'] == {}
    assert stats['average_orientation_diff'] == 0.0


def test_get_match_statistics():
    """Test match statistics calculation."""
    dest_face1 = create_mock_face()
    dest_face2 = create_mock_face()
    repo_face1 = create_test_face_entry('face1', 0)
    repo_face2 = create_test_face_entry('face2', 90)
    
    matches = [
        FaceMatch(dest_face1, repo_face1, 0.9, 5),
        FaceMatch(dest_face2, repo_face1, 0.8, 10),
        FaceMatch(dest_face1, repo_face2, 0.7, 15)
    ]
    
    mock_repo_manager = Mock(spec=RepositoryManager)
    matcher = RepositoryMatcher(mock_repo_manager)
    
    stats = matcher.get_match_statistics(matches)
    
    assert stats['total_matches'] == 3
    assert stats['average_confidence'] == pytest.approx(0.8, 0.01)
    assert stats['average_orientation_diff'] == 10.0
    assert stats['unique_repository_faces'] == 2
    assert stats['matches_by_face']['face1'] == 2
    assert stats['matches_by_face']['face2'] == 1
