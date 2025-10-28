"""Quality assessment module for repository faces."""

from typing import Dict, List, NamedTuple

import cv2
import numpy


class QualityMetrics(NamedTuple):
	"""Quality metrics for a face image."""
	sharpness: float
	brightness: float
	contrast: float
	resolution: float
	overall: float


class QualityAssessor:
	"""Assess quality of face images using multiple metrics."""

	def __init__(self):
		"""Initialize the quality assessor."""
		# Weights for overall quality calculation
		self.weights = {
			'sharpness': 0.35,
			'brightness': 0.20,
			'contrast': 0.25,
			'resolution': 0.20
		}

	def assess_face_quality(self, face_image: numpy.ndarray) -> QualityMetrics:
		"""
		Assess the quality of a face image using multiple metrics.

		Args:
			face_image: Face image as numpy array (BGR or RGB format)

		Returns:
			QualityMetrics with scores from 0.0 to 1.0 for each metric
		"""
		sharpness = self._calculate_sharpness(face_image)
		brightness = self._calculate_brightness(face_image)
		contrast = self._calculate_contrast(face_image)
		resolution = self._calculate_resolution(face_image)
		
		# Calculate overall quality as weighted average
		overall = (
			self.weights['sharpness'] * sharpness +
			self.weights['brightness'] * brightness +
			self.weights['contrast'] * contrast +
			self.weights['resolution'] * resolution
		)

		return QualityMetrics(
			sharpness=sharpness,
			brightness=brightness,
			contrast=contrast,
			resolution=resolution,
			overall=overall
		)

	def _calculate_sharpness(self, image: numpy.ndarray) -> float:
		"""
		Calculate sharpness using Laplacian variance.

		Args:
			image: Input image as numpy array

		Returns:
			Normalized sharpness score (0.0 to 1.0)
		"""
		# Convert to grayscale if needed
		if len(image.shape) == 3:
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		else:
			gray = image

		# Calculate Laplacian variance
		laplacian = cv2.Laplacian(gray, cv2.CV_64F)
		variance = laplacian.var()

		# Normalize to 0-1 range (empirically determined thresholds)
		# Values above 500 are considered very sharp
		normalized = min(variance / 500.0, 1.0)
		return float(normalized)

	def _calculate_brightness(self, image: numpy.ndarray) -> float:
		"""
		Calculate brightness score based on mean luminance.

		Args:
			image: Input image as numpy array

		Returns:
			Normalized brightness score (0.0 to 1.0, peak at mid-range)
		"""
		# Convert to LAB color space for luminance channel
		if len(image.shape) == 3:
			lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
			luminance = lab[:, :, 0]
		else:
			luminance = image

		mean_brightness = numpy.mean(luminance)

		# Optimal brightness is around 127 (middle of 0-255 range)
		# Score decreases as we move away from optimal
		deviation = abs(mean_brightness - 127.0)
		score = 1.0 - (deviation / 127.0)
		return float(max(0.0, score))

	def _calculate_contrast(self, image: numpy.ndarray) -> float:
		"""
		Calculate contrast using standard deviation.

		Args:
			image: Input image as numpy array

		Returns:
			Normalized contrast score (0.0 to 1.0)
		"""
		# Convert to grayscale if needed
		if len(image.shape) == 3:
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		else:
			gray = image

		# Calculate standard deviation as contrast measure
		std_dev = numpy.std(gray)

		# Normalize to 0-1 range (empirically determined thresholds)
		# Values above 64 are considered good contrast
		normalized = min(std_dev / 64.0, 1.0)
		return float(normalized)

	def _calculate_resolution(self, image: numpy.ndarray) -> float:
		"""
		Calculate resolution score based on image dimensions.

		Args:
			image: Input image as numpy array

		Returns:
			Normalized resolution score (0.0 to 1.0)
		"""
		height, width = image.shape[:2]
		area = height * width

		# Target resolution: 512x512 = 262144 pixels
		target_area = 512 * 512

		# Score based on how close to target
		if area >= target_area:
			score = 1.0
		else:
			score = area / target_area

		return float(score)

	def filter_by_quality_threshold(
		self,
		face_paths_with_quality: List[Dict[str, any]],
		threshold: float = 0.7
	) -> List[str]:
		"""
		Filter faces by quality threshold.

		Args:
			face_paths_with_quality: List of dicts with 'path' and 'quality' keys
			threshold: Minimum quality threshold (0.0 to 1.0)

		Returns:
			List of face paths that meet the quality threshold
		"""
		filtered = [
			item['path']
			for item in face_paths_with_quality
			if item.get('quality', {}).get('overall', 0.0) >= threshold
		]
		return filtered


def assess_face_from_path(face_path: str) -> QualityMetrics:
	"""
	Assess quality of a face image from file path.

	Args:
		face_path: Path to face image file

	Returns:
		QualityMetrics for the face image
	"""
	assessor = QualityAssessor()
	image = cv2.imread(face_path)
	
	if image is None:
		# Return zero quality if image cannot be loaded
		return QualityMetrics(
			sharpness=0.0,
			brightness=0.0,
			contrast=0.0,
			resolution=0.0,
			overall=0.0
		)
	
	return assessor.assess_face_quality(image)
