"""
Settings validator for FaceFusion configuration profiles.
"""

from typing import Any, Dict, List, Set

from facefusion_repository.types import ValidationResult


class ProfileValidator:
    """Validates settings against FaceFusion requirements."""

    # Valid options for each setting based on FaceFusion's state keys
    VALID_PROCESSORS: Set[str] = {
        'face_debugger',
        'face_enhancer',
        'face_swapper',
        'frame_colorizer',
        'frame_enhancer',
        'lip_syncer',
        'age_modifier',
        'expression_restorer'
    }

    VALID_FACE_DETECTOR_MODELS: Set[str] = {
        'many',
        'retinaface',
        'scrfd',
        'yoloface',
        'yunet'
    }

    VALID_FACE_DETECTOR_SIZES: Set[str] = {
        '160x160',
        '320x320',
        '480x480',
        '512x512',
        '640x640',
        '768x768',
        '1024x1024'
    }

    VALID_FACE_LANDMARKER_MODELS: Set[str] = {
        '2dfan4',
        'peppa_wutz'
    }

    VALID_FACE_SELECTOR_MODES: Set[str] = {
        'many',
        'one',
        'reference'
    }

    VALID_FACE_SELECTOR_ORDERS: Set[str] = {
        'best-worst',
        'worst-best',
        'left-right',
        'right-left',
        'small-large',
        'large-small'
    }

    VALID_FACE_SELECTOR_GENDERS: Set[str] = {
        'female',
        'male'
    }

    VALID_FACE_SELECTOR_RACES: Set[str] = {
        'white',
        'black',
        'latino',
        'asian',
        'middle_eastern',
        'indian'
    }

    VALID_FACE_MASK_TYPES: Set[str] = {
        'box',
        'occlusion',
        'region'
    }

    VALID_FACE_MASK_REGIONS: Set[str] = {
        'skin',
        'left-eyebrow',
        'right-eyebrow',
        'left-eye',
        'right-eye',
        'glasses',
        'nose',
        'mouth',
        'upper-lip',
        'lower-lip'
    }

    VALID_TEMP_FRAME_FORMATS: Set[str] = {
        'bmp',
        'jpg',
        'png'
    }

    VALID_OUTPUT_VIDEO_ENCODERS: Set[str] = {
        'libx264',
        'libx265',
        'libvpx-vp9',
        'h264_nvenc',
        'hevc_nvenc',
        'h264_amf',
        'hevc_amf'
    }

    VALID_OUTPUT_VIDEO_PRESETS: Set[str] = {
        'ultrafast',
        'superfast',
        'veryfast',
        'faster',
        'fast',
        'medium',
        'slow',
        'slower',
        'veryslow'
    }

    VALID_EXECUTION_PROVIDERS: Set[str] = {
        'cpu',
        'cuda',
        'coreml',
        'dml',
        'openvino',
        'tensorrt'
    }

    VALID_VIDEO_MEMORY_STRATEGIES: Set[str] = {
        'strict',
        'moderate',
        'tolerant'
    }

    VALID_FACE_OCCLUDER_MODELS: Set[str] = {
        'yoloface'
    }

    VALID_FACE_PARSER_MODELS: Set[str] = {
        'bisenet',
        'segnext'
    }

    VALID_VOICE_EXTRACTOR_MODELS: Set[str] = {
        'whisper'
    }

    VALID_OUTPUT_AUDIO_ENCODERS: Set[str] = {
        'aac',
        'libmp3lame',
        'libopus',
        'libvorbis'
    }

    @staticmethod
    def validate_settings(settings: Dict[str, Any]) -> ValidationResult:
        """
        Validate all settings.

        Args:
            settings: Settings dictionary to validate

        Returns:
            ValidationResult with validation status and messages
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Validate processors
        if 'processors' in settings:
            result = ProfileValidator.validate_processors(settings['processors'])
            if not result:
                errors.append(f"Invalid processors: {settings['processors']}")

        # Validate face detector settings
        if 'face_detector_model' in settings:
            if settings['face_detector_model'] not in ProfileValidator.VALID_FACE_DETECTOR_MODELS:
                errors.append(f"Invalid face_detector_model: {settings['face_detector_model']}")

        if 'face_detector_size' in settings:
            if settings['face_detector_size'] not in ProfileValidator.VALID_FACE_DETECTOR_SIZES:
                errors.append(f"Invalid face_detector_size: {settings['face_detector_size']}")

        if 'face_detector_score' in settings:
            score = settings['face_detector_score']
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                errors.append(f"Invalid face_detector_score: {score} (must be between 0 and 1)")

        # Validate face landmarker settings
        if 'face_landmarker_model' in settings:
            if settings['face_landmarker_model'] not in ProfileValidator.VALID_FACE_LANDMARKER_MODELS:
                errors.append(f"Invalid face_landmarker_model: {settings['face_landmarker_model']}")

        if 'face_landmarker_score' in settings:
            score = settings['face_landmarker_score']
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                errors.append(f"Invalid face_landmarker_score: {score} (must be between 0 and 1)")

        # Validate face selector settings
        if 'face_selector_mode' in settings:
            if settings['face_selector_mode'] not in ProfileValidator.VALID_FACE_SELECTOR_MODES:
                errors.append(f"Invalid face_selector_mode: {settings['face_selector_mode']}")

        if 'face_selector_order' in settings:
            if settings['face_selector_order'] not in ProfileValidator.VALID_FACE_SELECTOR_ORDERS:
                errors.append(f"Invalid face_selector_order: {settings['face_selector_order']}")

        if 'face_selector_gender' in settings:
            if settings['face_selector_gender'] not in ProfileValidator.VALID_FACE_SELECTOR_GENDERS:
                errors.append(f"Invalid face_selector_gender: {settings['face_selector_gender']}")

        if 'face_selector_race' in settings:
            if settings['face_selector_race'] not in ProfileValidator.VALID_FACE_SELECTOR_RACES:
                errors.append(f"Invalid face_selector_race: {settings['face_selector_race']}")

        if 'face_selector_age_start' in settings:
            age = settings['face_selector_age_start']
            if not isinstance(age, int) or age < 0 or age > 100:
                errors.append(f"Invalid face_selector_age_start: {age} (must be between 0 and 100)")

        if 'face_selector_age_end' in settings:
            age = settings['face_selector_age_end']
            if not isinstance(age, int) or age < 0 or age > 100:
                errors.append(f"Invalid face_selector_age_end: {age} (must be between 0 and 100)")

        # Validate face mask settings
        if 'face_mask_types' in settings:
            mask_types = settings['face_mask_types']
            if isinstance(mask_types, list):
                for mask_type in mask_types:
                    if mask_type not in ProfileValidator.VALID_FACE_MASK_TYPES:
                        errors.append(f"Invalid face_mask_type: {mask_type}")
            else:
                errors.append('face_mask_types must be a list')

        if 'face_mask_regions' in settings:
            regions = settings['face_mask_regions']
            if isinstance(regions, list):
                for region in regions:
                    if region not in ProfileValidator.VALID_FACE_MASK_REGIONS:
                        errors.append(f"Invalid face_mask_region: {region}")
            else:
                errors.append('face_mask_regions must be a list')

        if 'face_mask_blur' in settings:
            blur = settings['face_mask_blur']
            if not isinstance(blur, (int, float)) or blur < 0 or blur > 1:
                errors.append(f"Invalid face_mask_blur: {blur} (must be between 0 and 1)")

        if 'face_mask_padding' in settings:
            padding = settings['face_mask_padding']
            if not isinstance(padding, list) or len(padding) != 4:
                errors.append(f"Invalid face_mask_padding: {padding} (must be a list of 4 integers)")
            elif not all(isinstance(p, int) and -100 <= p <= 100 for p in padding):
                errors.append('Invalid face_mask_padding values (must be integers between -100 and 100)')

        # Validate execution settings
        if 'execution_providers' in settings:
            providers = settings['execution_providers']
            if isinstance(providers, list):
                for provider in providers:
                    if provider not in ProfileValidator.VALID_EXECUTION_PROVIDERS:
                        errors.append(f"Invalid execution_provider: {provider}")
            else:
                errors.append('execution_providers must be a list')

        if 'execution_thread_count' in settings:
            count = settings['execution_thread_count']
            if not isinstance(count, int) or count < 1 or count > 128:
                errors.append(f"Invalid execution_thread_count: {count} (must be between 1 and 128)")

        if 'video_memory_strategy' in settings:
            if settings['video_memory_strategy'] not in ProfileValidator.VALID_VIDEO_MEMORY_STRATEGIES:
                errors.append(f"Invalid video_memory_strategy: {settings['video_memory_strategy']}")

        # Validate output settings
        if 'output_image_quality' in settings:
            quality = settings['output_image_quality']
            if not isinstance(quality, int) or quality < 0 or quality > 100:
                errors.append(f"Invalid output_image_quality: {quality} (must be between 0 and 100)")

        if 'output_video_encoder' in settings:
            if settings['output_video_encoder'] not in ProfileValidator.VALID_OUTPUT_VIDEO_ENCODERS:
                errors.append(f"Invalid output_video_encoder: {settings['output_video_encoder']}")

        if 'output_video_preset' in settings:
            if settings['output_video_preset'] not in ProfileValidator.VALID_OUTPUT_VIDEO_PRESETS:
                errors.append(f"Invalid output_video_preset: {settings['output_video_preset']}")

        if 'output_video_quality' in settings:
            quality = settings['output_video_quality']
            if not isinstance(quality, int) or quality < 0 or quality > 100:
                errors.append(f"Invalid output_video_quality: {quality} (must be between 0 and 100)")

        # Validate temp frame format
        if 'temp_frame_format' in settings:
            if settings['temp_frame_format'] not in ProfileValidator.VALID_TEMP_FRAME_FORMATS:
                errors.append(f"Invalid temp_frame_format: {settings['temp_frame_format']}")

        # Add warnings for missing recommended settings
        recommended_settings = ['processors', 'face_detector_model', 'face_detector_score']
        for setting in recommended_settings:
            if setting not in settings:
                warnings.append(f"Recommended setting missing: {setting}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_processors(processors: List[str]) -> bool:
        """
        Validate processor list.

        Args:
            processors: List of processor names

        Returns:
            True if all processors are valid
        """
        if not isinstance(processors, list):
            return False

        return all(proc in ProfileValidator.VALID_PROCESSORS for proc in processors)

    @staticmethod
    def validate_models(settings: Dict[str, Any]) -> bool:
        """
        Validate model selections.

        Args:
            settings: Settings dictionary

        Returns:
            True if model selections are valid
        """
        # Check face detector model
        if 'face_detector_model' in settings:
            if settings['face_detector_model'] not in ProfileValidator.VALID_FACE_DETECTOR_MODELS:
                return False

        # Check face landmarker model
        if 'face_landmarker_model' in settings:
            if settings['face_landmarker_model'] not in ProfileValidator.VALID_FACE_LANDMARKER_MODELS:
                return False

        return True

    @staticmethod
    def get_available_options() -> Dict[str, List[Any]]:
        """
        Get all available options for each setting.

        Returns:
            Dictionary mapping setting names to available options
        """
        return {
            'processors': sorted(ProfileValidator.VALID_PROCESSORS),
            'face_detector_model': sorted(ProfileValidator.VALID_FACE_DETECTOR_MODELS),
            'face_detector_size': sorted(ProfileValidator.VALID_FACE_DETECTOR_SIZES),
            'face_landmarker_model': sorted(ProfileValidator.VALID_FACE_LANDMARKER_MODELS),
            'face_selector_mode': sorted(ProfileValidator.VALID_FACE_SELECTOR_MODES),
            'face_selector_order': sorted(ProfileValidator.VALID_FACE_SELECTOR_ORDERS),
            'face_selector_gender': sorted(ProfileValidator.VALID_FACE_SELECTOR_GENDERS),
            'face_selector_race': sorted(ProfileValidator.VALID_FACE_SELECTOR_RACES),
            'face_mask_types': sorted(ProfileValidator.VALID_FACE_MASK_TYPES),
            'face_mask_regions': sorted(ProfileValidator.VALID_FACE_MASK_REGIONS),
            'temp_frame_format': sorted(ProfileValidator.VALID_TEMP_FRAME_FORMATS),
            'output_video_encoder': sorted(ProfileValidator.VALID_OUTPUT_VIDEO_ENCODERS),
            'output_video_preset': sorted(ProfileValidator.VALID_OUTPUT_VIDEO_PRESETS),
            'execution_providers': sorted(ProfileValidator.VALID_EXECUTION_PROVIDERS),
            'video_memory_strategy': sorted(ProfileValidator.VALID_VIDEO_MEMORY_STRATEGIES),
            'face_occluder_model': sorted(ProfileValidator.VALID_FACE_OCCLUDER_MODELS),
            'face_parser_model': sorted(ProfileValidator.VALID_FACE_PARSER_MODELS),
            'voice_extractor_model': sorted(ProfileValidator.VALID_VOICE_EXTRACTOR_MODELS),
            'output_audio_encoder': sorted(ProfileValidator.VALID_OUTPUT_AUDIO_ENCODERS)
        }
