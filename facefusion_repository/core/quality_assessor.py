"""Face quality assessment for repository"""

from typing import Any, Dict

import numpy
from numpy.typing import NDArray

from facefusion_repository.types import QualityMetrics


class QualityAssessor:
	"""Assesses face quality for repository addition"""
	
	def assess_quality(self, vision_frame : NDArray[Any], face_data : Dict[str, Any]) -> QualityMetrics:
		"""Assess the quality of a face image"""
		sharpness = self._calculate_sharpness(vision_frame)
		brightness = self._calculate_brightness(vision_frame)
		overall_quality = self._calculate_overall_quality(sharpness, brightness, face_data)
		has_occlusion = self._check_occlusion(face_data)
		
		return\
		{
			'sharpness': float(sharpness),
			'brightness': float(brightness),
			'overall_quality': float(overall_quality),
			'has_occlusion': bool(has_occlusion)
		}
	
	def _calculate_sharpness(self, vision_frame : NDArray[Any]) -> float:
		"""Calculate image sharpness using Laplacian variance"""
		try:
			if len(vision_frame.shape) == 3:
				gray = numpy.mean(vision_frame, axis=2)
			else:
				gray = vision_frame
			
			laplacian = numpy.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
			filtered = numpy.abs(numpy.convolve(gray.flatten(), laplacian.flatten(), mode='same'))
			sharpness = numpy.var(filtered)
			
			# Normalize to 0-1 range
			normalized = min(sharpness / 1000.0, 1.0)
			return normalized
		except Exception:
			return 0.5
	
	def _calculate_brightness(self, vision_frame : NDArray[Any]) -> float:
		"""Calculate average brightness"""
		try:
			mean_brightness = numpy.mean(vision_frame) / 255.0
			
			# Prefer moderate brightness (0.3-0.7 range is ideal)
			if 0.3 <= mean_brightness <= 0.7:
				score = 1.0
			elif mean_brightness < 0.3:
				score = mean_brightness / 0.3
			else:
				score = (1.0 - mean_brightness) / 0.3
			
			return max(0.0, min(1.0, score))
		except Exception:
			return 0.5
	
	def _check_occlusion(self, face_data : Dict[str, Any]) -> bool:
		"""Check if face has occlusion"""
		# Placeholder - would integrate with face_masker in real implementation
		return False
	
	def _calculate_overall_quality(self, sharpness : float, brightness : float, face_data : Dict[str, Any]) -> float:
		"""Calculate overall quality score"""
		# Weight different factors
		weights =\
		{
			'sharpness': 0.4,
			'brightness': 0.3,
			'detector_score': 0.3
		}
		
		detector_score = face_data.get('detector_score', 0.5)
		
		overall = (
			sharpness * weights['sharpness'] +
			brightness * weights['brightness'] +
			detector_score * weights['detector_score']
		)
		
		return max(0.0, min(1.0, overall))
	
	def is_quality_acceptable(self, quality : QualityMetrics, min_quality : float = 0.5) -> bool:
		"""Check if quality meets minimum threshold"""
		return quality['overall_quality'] >= min_quality and not quality['has_occlusion']
