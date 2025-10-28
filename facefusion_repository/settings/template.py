"""
Settings templates for common FaceFusion configurations.
"""

from typing import Any, Dict


class SettingsTemplate:
    """Provides default settings templates for common use cases."""

    @staticmethod
    def get_default_face_swap() -> Dict[str, Any]:
        """
        Get default settings for basic face swapping.

        Returns:
            Settings dictionary for basic face swap
        """
        return {
            'processors': ['face_swapper'],
            'face_detector_model': 'yoloface',
            'face_detector_size': '640x640',
            'face_detector_score': 0.5,
            'face_landmarker_model': '2dfan4',
            'face_landmarker_score': 0.5,
            'face_selector_mode': 'one',
            'face_selector_order': 'best-worst',
            'face_mask_types': ['box'],
            'face_mask_blur': 0.3,
            'face_mask_padding': [0, 0, 0, 0],
            'execution_providers': ['cpu'],
            'execution_thread_count': 4,
            'output_video_encoder': 'libx264',
            'output_video_preset': 'medium',
            'output_video_quality': 80,
            'output_image_quality': 80,
            'temp_frame_format': 'jpg',
            'keep_temp': False
        }

    @staticmethod
    def get_high_quality_swap() -> Dict[str, Any]:
        """
        Get settings for high-quality face swapping.

        Returns:
            Settings dictionary for high-quality face swap
        """
        return {
            'processors': ['face_swapper', 'face_enhancer'],
            'face_detector_model': 'yoloface',
            'face_detector_size': '640x640',
            'face_detector_score': 0.6,
            'face_landmarker_model': '2dfan4',
            'face_landmarker_score': 0.6,
            'face_selector_mode': 'one',
            'face_selector_order': 'best-worst',
            'face_mask_types': ['box', 'region'],
            'face_mask_regions': ['skin', 'left-eye', 'right-eye', 'nose', 'mouth'],
            'face_mask_blur': 0.4,
            'face_mask_padding': [0, 10, 0, 10],
            'execution_providers': ['cpu'],
            'execution_thread_count': 8,
            'output_video_encoder': 'libx264',
            'output_video_preset': 'slow',
            'output_video_quality': 95,
            'output_image_quality': 95,
            'temp_frame_format': 'png',
            'keep_temp': False
        }

    @staticmethod
    def get_fast_preview() -> Dict[str, Any]:
        """
        Get settings for fast preview/testing.

        Returns:
            Settings dictionary for fast preview
        """
        return {
            'processors': ['face_swapper'],
            'face_detector_model': 'yoloface',
            'face_detector_size': '320x320',
            'face_detector_score': 0.4,
            'face_landmarker_model': '2dfan4',
            'face_landmarker_score': 0.4,
            'face_selector_mode': 'one',
            'face_selector_order': 'best-worst',
            'face_mask_types': ['box'],
            'face_mask_blur': 0.2,
            'face_mask_padding': [0, 0, 0, 0],
            'execution_providers': ['cpu'],
            'execution_thread_count': 2,
            'output_video_encoder': 'libx264',
            'output_video_preset': 'ultrafast',
            'output_video_quality': 60,
            'output_image_quality': 60,
            'temp_frame_format': 'jpg',
            'keep_temp': False
        }

    @staticmethod
    def get_gpu_accelerated() -> Dict[str, Any]:
        """
        Get settings optimized for GPU acceleration.

        Returns:
            Settings dictionary for GPU acceleration
        """
        return {
            'processors': ['face_swapper'],
            'face_detector_model': 'yoloface',
            'face_detector_size': '640x640',
            'face_detector_score': 0.5,
            'face_landmarker_model': '2dfan4',
            'face_landmarker_score': 0.5,
            'face_selector_mode': 'one',
            'face_selector_order': 'best-worst',
            'face_mask_types': ['box', 'region'],
            'face_mask_blur': 0.3,
            'face_mask_padding': [0, 0, 0, 0],
            'execution_providers': ['cuda'],
            'execution_thread_count': 4,
            'video_memory_strategy': 'moderate',
            'output_video_encoder': 'h264_nvenc',
            'output_video_preset': 'medium',
            'output_video_quality': 80,
            'output_image_quality': 80,
            'temp_frame_format': 'jpg',
            'keep_temp': False
        }

    @staticmethod
    def get_multi_face_swap() -> Dict[str, Any]:
        """
        Get settings for swapping multiple faces.

        Returns:
            Settings dictionary for multi-face swap
        """
        return {
            'processors': ['face_swapper'],
            'face_detector_model': 'yoloface',
            'face_detector_size': '640x640',
            'face_detector_score': 0.5,
            'face_landmarker_model': '2dfan4',
            'face_landmarker_score': 0.5,
            'face_selector_mode': 'many',
            'face_selector_order': 'best-worst',
            'face_mask_types': ['box', 'region'],
            'face_mask_blur': 0.3,
            'face_mask_padding': [0, 0, 0, 0],
            'execution_providers': ['cpu'],
            'execution_thread_count': 4,
            'output_video_encoder': 'libx264',
            'output_video_preset': 'medium',
            'output_video_quality': 80,
            'output_image_quality': 80,
            'temp_frame_format': 'jpg',
            'keep_temp': False
        }

    @staticmethod
    def get_reference_face_swap() -> Dict[str, Any]:
        """
        Get settings for reference-based face swapping.

        Returns:
            Settings dictionary for reference face swap
        """
        return {
            'processors': ['face_swapper'],
            'face_detector_model': 'yoloface',
            'face_detector_size': '640x640',
            'face_detector_score': 0.5,
            'face_landmarker_model': '2dfan4',
            'face_landmarker_score': 0.5,
            'face_selector_mode': 'reference',
            'face_selector_order': 'best-worst',
            'reference_face_distance': 0.6,
            'face_mask_types': ['box', 'region'],
            'face_mask_blur': 0.3,
            'face_mask_padding': [0, 0, 0, 0],
            'execution_providers': ['cpu'],
            'execution_thread_count': 4,
            'output_video_encoder': 'libx264',
            'output_video_preset': 'medium',
            'output_video_quality': 80,
            'output_image_quality': 80,
            'temp_frame_format': 'jpg',
            'keep_temp': False
        }

    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        """
        Get all available templates.

        Returns:
            Dictionary mapping template names to settings
        """
        return {
            'default_swap': SettingsTemplate.get_default_face_swap(),
            'high_quality': SettingsTemplate.get_high_quality_swap(),
            'fast_preview': SettingsTemplate.get_fast_preview(),
            'gpu_accelerated': SettingsTemplate.get_gpu_accelerated(),
            'multi_face': SettingsTemplate.get_multi_face_swap(),
            'reference_face': SettingsTemplate.get_reference_face_swap()
        }

    @staticmethod
    def get_template_descriptions() -> Dict[str, str]:
        """
        Get descriptions for all templates.

        Returns:
            Dictionary mapping template names to descriptions
        """
        return {
            'default_swap': 'Basic face swap with balanced quality and performance',
            'high_quality': 'High-quality face swap with face enhancement',
            'fast_preview': 'Fast preview mode for testing',
            'gpu_accelerated': 'Optimized for GPU acceleration',
            'multi_face': 'Swap multiple faces in the same frame',
            'reference_face': 'Use reference face for selective swapping'
        }
