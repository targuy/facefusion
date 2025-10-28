"""
Settings validator for FaceFusion configuration.
"""

from typing import Any, Dict, List

from facefusion_repository.types import ValidationResult


class SettingsValidator:
    """Validates settings against FaceFusion requirements."""

    # Valid processor types
    VALID_PROCESSORS = [
        'face_swapper',
        'face_enhancer',
        'face_debugger',
        'frame_enhancer',
        'age_modifier',
        'expression_restorer',
        'lip_syncer',
        'frame_colorizer',
        'face_editor'
    ]

    # Valid face selector modes
    VALID_SELECTOR_MODES = ['one', 'many', 'reference']

    # Valid face selector orders
    VALID_SELECTOR_ORDERS = [
        'left-right',
        'right-left',
        'top-bottom',
        'bottom-top',
        'small-large',
        'large-small',
        'best-worst',
        'worst-best'
    ]

    # Valid face detector models
    VALID_DETECTOR_MODELS = ['yolo_face', 'retinaface', 'scrfd', 'many', 'yunet']

    # Valid face detector sizes
    VALID_DETECTOR_SIZES = ['320x320', '640x640', '960x960', '1280x1280']

    # Valid face landmarker models
    VALID_LANDMARKER_MODELS = ['2dfan4', 'peppa_wutz']

    # Valid face masker types
    VALID_MASKER_TYPES = ['box', 'occlusion', 'region']

    @classmethod
    def validate_settings(cls, settings: Dict[str, Any]) -> ValidationResult:
        """
        Validate all settings.

        Args:
            settings: Settings dictionary

        Returns:
            ValidationResult with validation status and messages
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Validate processors
        if 'processors' in settings:
            if not cls.validate_processors(settings['processors']):
                errors.append(f'Invalid processors: {settings["processors"]}')

        # Validate face selector mode
        if 'face_selector_mode' in settings:
            if settings['face_selector_mode'] not in cls.VALID_SELECTOR_MODES:
                errors.append(f'Invalid face_selector_mode: {settings["face_selector_mode"]}')

        # Validate face selector order
        if 'face_selector_order' in settings:
            if settings['face_selector_order'] not in cls.VALID_SELECTOR_ORDERS:
                errors.append(f'Invalid face_selector_order: {settings["face_selector_order"]}')

        # Validate face detector model
        if 'face_detector_model' in settings:
            if settings['face_detector_model'] not in cls.VALID_DETECTOR_MODELS:
                errors.append(f'Invalid face_detector_model: {settings["face_detector_model"]}')

        # Validate face detector size
        if 'face_detector_size' in settings:
            if settings['face_detector_size'] not in cls.VALID_DETECTOR_SIZES:
                errors.append(f'Invalid face_detector_size: {settings["face_detector_size"]}')

        # Validate face detector score
        if 'face_detector_score' in settings:
            score = settings['face_detector_score']
            if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                errors.append(f'Invalid face_detector_score: {score} (must be 0.0-1.0)')

        # Validate face landmarker model
        if 'face_landmarker_model' in settings:
            if settings['face_landmarker_model'] not in cls.VALID_LANDMARKER_MODELS:
                errors.append(f'Invalid face_landmarker_model: {settings["face_landmarker_model"]}')

        # Validate face landmarker score
        if 'face_landmarker_score' in settings:
            score = settings['face_landmarker_score']
            if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                errors.append(f'Invalid face_landmarker_score: {score} (must be 0.0-1.0)')

        # Validate face masker types
        if 'face_masker_types' in settings:
            if not cls.validate_masker_types(settings['face_masker_types']):
                errors.append(f'Invalid face_masker_types: {settings["face_masker_types"]}')

        # Validate face mask blur
        if 'face_mask_blur' in settings:
            blur = settings['face_mask_blur']
            if not isinstance(blur, (int, float)) or not (0.0 <= blur <= 1.0):
                errors.append(f'Invalid face_mask_blur: {blur} (must be 0.0-1.0)')

        # Validate face mask padding
        if 'face_mask_padding' in settings:
            padding = settings['face_mask_padding']
            if not isinstance(padding, list) or len(padding) != 4:
                errors.append(f'Invalid face_mask_padding: {padding} (must be list of 4 integers)')
            elif not all(isinstance(p, int) for p in padding):
                errors.append(f'Invalid face_mask_padding: {padding} (all values must be integers)')

        # Check for unknown settings (warnings only)
        known_settings = {
            'processors', 'face_selector_mode', 'face_selector_order',
            'face_detector_model', 'face_detector_size', 'face_detector_score',
            'face_landmarker_model', 'face_landmarker_score',
            'face_masker_types', 'face_mask_blur', 'face_mask_padding',
            'face_analyser_order', 'face_analyser_age', 'face_analyser_gender',
            'reference_face_distance', 'reference_face_position', 'reference_frame_number',
            'output_image_quality', 'output_image_resolution', 'output_video_encoder',
            'output_video_preset', 'output_video_quality', 'output_video_resolution',
            'output_audio_encoder', 'output_path', 'temp_frame_format',
            'keep_temp', 'skip_audio', 'execution_device_id', 'execution_providers',
            'execution_thread_count', 'execution_queue_count', 'max_memory',
            'video_memory_strategy', 'system_memory_limit'
        }

        for key in settings:
            if key not in known_settings:
                warnings.append(f'Unknown setting: {key}')

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @classmethod
    def validate_processors(cls, processors: List[str]) -> bool:
        """
        Validate processor list.

        Args:
            processors: List of processor names

        Returns:
            True if all processors are valid
        """
        if not isinstance(processors, list):
            return False

        return all(p in cls.VALID_PROCESSORS for p in processors)

    @classmethod
    def validate_masker_types(cls, masker_types: List[str]) -> bool:
        """
        Validate masker types list.

        Args:
            masker_types: List of masker type names

        Returns:
            True if all masker types are valid
        """
        if not isinstance(masker_types, list):
            return False

        return all(m in cls.VALID_MASKER_TYPES for m in masker_types)

    @classmethod
    def get_available_options(cls) -> Dict[str, List[Any]]:
        """
        Get all available options for each setting.

        Returns:
            Dictionary mapping setting names to available values
        """
        return {
            'processors': cls.VALID_PROCESSORS,
            'face_selector_mode': cls.VALID_SELECTOR_MODES,
            'face_selector_order': cls.VALID_SELECTOR_ORDERS,
            'face_detector_model': cls.VALID_DETECTOR_MODELS,
            'face_detector_size': cls.VALID_DETECTOR_SIZES,
            'face_landmarker_model': cls.VALID_LANDMARKER_MODELS,
            'face_masker_types': cls.VALID_MASKER_TYPES
        }
