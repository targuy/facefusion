"""Tests for quality assessment functionality."""

import tempfile
from pathlib import Path

import cv2
import numpy
import pytest

from facefusion_repository.quality_assessor import (
	QualityAssessor,
	QualityMetrics,
	assess_face_from_path
)


@pytest.fixture
def sample_image():
	"""Create a sample test image."""
	# Create a 512x512 RGB image with reasonable quality
	image = numpy.random.randint(50, 200, (512, 512, 3), dtype=numpy.uint8)
	return image


@pytest.fixture
def low_quality_image():
	"""Create a low quality test image."""
	# Create a small, low contrast image
	image = numpy.ones((128, 128, 3), dtype=numpy.uint8) * 100
	return image


@pytest.fixture
def high_quality_image():
	"""Create a high quality test image."""
	# Create a large, high contrast, sharp image
	image = numpy.zeros((640, 640, 3), dtype=numpy.uint8)
	# Add high contrast patterns
	image[::2, ::2] = 255
	image[1::2, 1::2] = 0
	return image


def test_quality_assessor_initialization():
	"""Test quality assessor initialization."""
	assessor = QualityAssessor()
	assert assessor is not None
	assert 'sharpness' in assessor.weights
	assert 'brightness' in assessor.weights
	assert 'contrast' in assessor.weights
	assert 'resolution' in assessor.weights


def test_assess_face_quality_returns_metrics(sample_image):
	"""Test that quality assessment returns proper metrics."""
	assessor = QualityAssessor()
	metrics = assessor.assess_face_quality(sample_image)
	
	assert isinstance(metrics, QualityMetrics)
	assert 0.0 <= metrics.sharpness <= 1.0
	assert 0.0 <= metrics.brightness <= 1.0
	assert 0.0 <= metrics.contrast <= 1.0
	assert 0.0 <= metrics.resolution <= 1.0
	assert 0.0 <= metrics.overall <= 1.0


def test_assess_sharpness_calculation(sample_image):
	"""Test sharpness calculation."""
	assessor = QualityAssessor()
	sharpness = assessor._calculate_sharpness(sample_image)
	assert isinstance(sharpness, float)
	assert 0.0 <= sharpness <= 1.0


def test_assess_brightness_calculation(sample_image):
	"""Test brightness calculation."""
	assessor = QualityAssessor()
	brightness = assessor._calculate_brightness(sample_image)
	assert isinstance(brightness, float)
	assert 0.0 <= brightness <= 1.0


def test_assess_contrast_calculation(sample_image):
	"""Test contrast calculation."""
	assessor = QualityAssessor()
	contrast = assessor._calculate_contrast(sample_image)
	assert isinstance(contrast, float)
	assert 0.0 <= contrast <= 1.0


def test_assess_resolution_calculation(sample_image):
	"""Test resolution calculation."""
	assessor = QualityAssessor()
	resolution = assessor._calculate_resolution(sample_image)
	assert isinstance(resolution, float)
	assert 0.0 <= resolution <= 1.0


def test_high_quality_image_scores_higher(high_quality_image, low_quality_image):
	"""Test that high quality images score higher than low quality ones."""
	assessor = QualityAssessor()
	high_metrics = assessor.assess_face_quality(high_quality_image)
	low_metrics = assessor.assess_face_quality(low_quality_image)
	
	# High quality should have better resolution
	assert high_metrics.resolution >= low_metrics.resolution
	# High quality should have better contrast
	assert high_metrics.contrast >= low_metrics.contrast


def test_filter_by_quality_threshold():
	"""Test filtering faces by quality threshold."""
	assessor = QualityAssessor()
	
	faces_with_quality = [
		{'path': 'face1.jpg', 'quality': {'overall': 0.9}},
		{'path': 'face2.jpg', 'quality': {'overall': 0.5}},
		{'path': 'face3.jpg', 'quality': {'overall': 0.8}},
		{'path': 'face4.jpg', 'quality': {'overall': 0.3}},
	]
	
	filtered = assessor.filter_by_quality_threshold(faces_with_quality, threshold=0.7)
	
	assert len(filtered) == 2
	assert 'face1.jpg' in filtered
	assert 'face3.jpg' in filtered
	assert 'face2.jpg' not in filtered
	assert 'face4.jpg' not in filtered


def test_assess_face_from_path_with_valid_image(sample_image):
	"""Test assessing face quality from file path."""
	with tempfile.TemporaryDirectory() as temp_dir:
		image_path = Path(temp_dir) / 'test_face.jpg'
		cv2.imwrite(str(image_path), sample_image)
		
		metrics = assess_face_from_path(str(image_path))
		
		assert isinstance(metrics, QualityMetrics)
		assert 0.0 <= metrics.overall <= 1.0


def test_assess_face_from_path_with_invalid_path():
	"""Test assessing face quality from invalid path."""
	metrics = assess_face_from_path('nonexistent_file.jpg')
	
	# Should return zero quality for invalid files
	assert metrics.overall == 0.0
	assert metrics.sharpness == 0.0
	assert metrics.brightness == 0.0
	assert metrics.contrast == 0.0
	assert metrics.resolution == 0.0


def test_resolution_score_for_target_size():
	"""Test that target resolution (512x512) gets full score."""
	assessor = QualityAssessor()
	target_image = numpy.zeros((512, 512, 3), dtype=numpy.uint8)
	
	resolution = assessor._calculate_resolution(target_image)
	assert resolution == 1.0


def test_resolution_score_for_smaller_size():
	"""Test that smaller images get lower resolution scores."""
	assessor = QualityAssessor()
	small_image = numpy.zeros((256, 256, 3), dtype=numpy.uint8)
	
	resolution = assessor._calculate_resolution(small_image)
	assert resolution < 1.0
	assert resolution == 0.25  # 256*256 / (512*512) = 0.25


def test_overall_quality_is_weighted_average(sample_image):
	"""Test that overall quality is a weighted average of metrics."""
	assessor = QualityAssessor()
	metrics = assessor.assess_face_quality(sample_image)
	
	# Calculate expected overall
	expected_overall = (
		assessor.weights['sharpness'] * metrics.sharpness +
		assessor.weights['brightness'] * metrics.brightness +
		assessor.weights['contrast'] * metrics.contrast +
		assessor.weights['resolution'] * metrics.resolution
	)
	
	# Should be approximately equal (allowing for floating point errors)
	assert abs(metrics.overall - expected_overall) < 0.0001
