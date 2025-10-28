"""
Tests for FaceFusion Repository System - Destination Extractor.
"""

import numpy as np
import pytest
from unittest.mock import Mock, patch, MagicMock

from facefusion.types import Face
from facefusion_repository.destination.extractor import FaceExtractor
from facefusion_repository.types import QualityMetrics


def create_mock_face(angle: float = 0.0, score: float = 0.9) -> Face:
    """Create a mock Face object for testing."""
    face = Mock(spec=Face)
    face.angle = angle
    face.score_set = {'detector': score}
    face.bounding_box = [100, 100, 200, 200]
    face.landmark_set = {
        '5': np.array([[150, 120], [180, 120], [165, 150], [155, 170], [175, 170]]),
        '68': np.zeros((68, 2))
    }
    face.embedding = np.random.rand(512)
    return face


def create_mock_vision_frame(width: int = 640, height: int = 480) -> np.ndarray:
    """Create a mock vision frame."""
    return np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)


@patch('facefusion_repository.destination.extractor.read_static_image')
@patch('facefusion_repository.destination.extractor.face_analyser.get_many_faces')
@patch('facefusion_repository.destination.extractor.QualityAssessor.assess_face')
@patch('facefusion_repository.destination.extractor.QualityAssessor.is_acceptable_quality')
def test_extract_from_image_success(
    mock_is_acceptable,
    mock_assess,
    mock_get_faces,
    mock_read_image
):
    """Test successful face extraction from image."""
    # Setup mocks
    mock_vision_frame = create_mock_vision_frame()
    mock_read_image.return_value = mock_vision_frame
    
    mock_face = create_mock_face()
    mock_get_faces.return_value = [mock_face]
    
    mock_quality = QualityMetrics(
        resolution=(512, 512),
        sharpness=0.7,
        detector_score=0.9,
        brightness=0.6,
        contrast=0.5,
        overall_quality=0.75
    )
    mock_assess.return_value = mock_quality
    mock_is_acceptable.return_value = True
    
    # Test extraction
    result = FaceExtractor.extract_from_image('test.jpg')
    
    assert len(result) == 1
    assert result[0] == mock_face
    mock_read_image.assert_called_once_with('test.jpg')
    mock_get_faces.assert_called_once()


@patch('facefusion_repository.destination.extractor.read_static_image')
def test_extract_from_image_no_file(mock_read_image):
    """Test extraction when image file cannot be read."""
    mock_read_image.return_value = None
    
    result = FaceExtractor.extract_from_image('nonexistent.jpg')
    
    assert result == []


@patch('facefusion_repository.destination.extractor.face_analyser.get_many_faces')
@patch('facefusion_repository.destination.extractor.QualityAssessor.assess_face')
@patch('facefusion_repository.destination.extractor.QualityAssessor.is_acceptable_quality')
def test_extract_from_frame_with_quality_filter(
    mock_is_acceptable,
    mock_assess,
    mock_get_faces
):
    """Test frame extraction with quality filtering."""
    mock_vision_frame = create_mock_vision_frame()
    
    # Create two faces with different qualities
    face1 = create_mock_face(score=0.9)
    face2 = create_mock_face(score=0.4)
    mock_get_faces.return_value = [face1, face2]
    
    # Only first face passes quality check
    mock_assess.side_effect = [
        QualityMetrics((512, 512), 0.7, 0.9, 0.6, 0.5, 0.75),
        QualityMetrics((256, 256), 0.3, 0.4, 0.5, 0.3, 0.35)
    ]
    mock_is_acceptable.side_effect = [True, False]
    
    result = FaceExtractor.extract_from_frame(mock_vision_frame)
    
    assert len(result) == 1
    assert result[0] == face1


@patch('facefusion_repository.destination.extractor.QualityAssessor.assess_face')
def test_get_face_quality(mock_assess):
    """Test getting face quality metrics."""
    mock_vision_frame = create_mock_vision_frame()
    mock_face = create_mock_face()
    
    expected_quality = QualityMetrics(
        resolution=(512, 512),
        sharpness=0.7,
        detector_score=0.9,
        brightness=0.6,
        contrast=0.5,
        overall_quality=0.75
    )
    mock_assess.return_value = expected_quality
    
    result = FaceExtractor.get_face_quality(mock_vision_frame, mock_face)
    
    assert result == expected_quality
    mock_assess.assert_called_once_with(mock_vision_frame, mock_face)


def test_is_quality_acceptable():
    """Test quality acceptance check."""
    quality = QualityMetrics(
        resolution=(512, 512),
        sharpness=0.7,
        detector_score=0.9,
        brightness=0.6,
        contrast=0.5,
        overall_quality=0.75
    )
    
    with patch('facefusion_repository.destination.extractor.QualityAssessor.is_acceptable_quality') as mock_check:
        mock_check.return_value = True
        
        result = FaceExtractor.is_quality_acceptable(quality)
        
        assert result is True
        mock_check.assert_called_once()
