"""
Tests for FaceFusion Repository System - Settings Validator.
"""

import pytest

from facefusion_repository.settings.validator import ProfileValidator


def test_validate_valid_settings() -> None:
    """Test validating correct settings."""
    settings = {
        'processors': ['face_swapper'],
        'face_detector_model': 'yoloface',
        'face_detector_size': '640x640',
        'face_detector_score': 0.5,
        'execution_providers': ['cpu']
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is True
    assert len(result.errors) == 0


def test_validate_invalid_processor() -> None:
    """Test validation fails for invalid processor."""
    settings = {
        'processors': ['invalid_processor']
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('processors' in err for err in result.errors)


def test_validate_invalid_face_detector_model() -> None:
    """Test validation fails for invalid face detector model."""
    settings = {
        'face_detector_model': 'invalid_model'
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('face_detector_model' in err for err in result.errors)


def test_validate_invalid_face_detector_size() -> None:
    """Test validation fails for invalid face detector size."""
    settings = {
        'face_detector_size': '999x999'
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('face_detector_size' in err for err in result.errors)


def test_validate_invalid_face_detector_score() -> None:
    """Test validation fails for out-of-range score."""
    settings = {
        'face_detector_score': 1.5
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('face_detector_score' in err for err in result.errors)


def test_validate_invalid_execution_providers() -> None:
    """Test validation fails for invalid execution provider."""
    settings = {
        'execution_providers': ['invalid_provider']
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('execution_provider' in err for err in result.errors)


def test_validate_invalid_execution_providers_not_list() -> None:
    """Test validation fails when execution_providers is not a list."""
    settings = {
        'execution_providers': 'cpu'
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('execution_providers must be a list' in err for err in result.errors)


def test_validate_invalid_face_mask_types() -> None:
    """Test validation fails for invalid face mask type."""
    settings = {
        'face_mask_types': ['invalid_mask']
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('face_mask_type' in err for err in result.errors)


def test_validate_invalid_face_mask_blur() -> None:
    """Test validation fails for out-of-range blur."""
    settings = {
        'face_mask_blur': 2.0
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('face_mask_blur' in err for err in result.errors)


def test_validate_invalid_face_mask_padding() -> None:
    """Test validation fails for invalid padding."""
    settings = {
        'face_mask_padding': [0, 0]  # Should be 4 values
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('face_mask_padding' in err for err in result.errors)


def test_validate_invalid_execution_thread_count() -> None:
    """Test validation fails for invalid thread count."""
    settings = {
        'execution_thread_count': 0
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('execution_thread_count' in err for err in result.errors)


def test_validate_warnings() -> None:
    """Test validation warnings for missing recommended settings."""
    settings = {
        'face_mask_blur': 0.3
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is True
    assert len(result.warnings) > 0


def test_validate_processors() -> None:
    """Test processor validation."""
    assert ProfileValidator.validate_processors(['face_swapper']) is True
    assert ProfileValidator.validate_processors(['face_swapper', 'face_enhancer']) is True
    assert ProfileValidator.validate_processors(['invalid_processor']) is False
    assert ProfileValidator.validate_processors('not_a_list') is False  # type: ignore


def test_validate_models() -> None:
    """Test model validation."""
    settings = {
        'face_detector_model': 'yoloface',
        'face_landmarker_model': '2dfan4'
    }
    assert ProfileValidator.validate_models(settings) is True

    settings = {
        'face_detector_model': 'invalid_model'
    }
    assert ProfileValidator.validate_models(settings) is False


def test_get_available_options() -> None:
    """Test getting available options."""
    options = ProfileValidator.get_available_options()

    assert 'processors' in options
    assert 'face_detector_model' in options
    assert 'execution_providers' in options

    # Check that lists are not empty
    assert len(options['processors']) > 0
    assert len(options['face_detector_model']) > 0

    # Check specific values
    assert 'face_swapper' in options['processors']
    assert 'yoloface' in options['face_detector_model']
    assert 'cpu' in options['execution_providers']


def test_validate_face_selector_settings() -> None:
    """Test validation of face selector settings."""
    settings = {
        'face_selector_mode': 'one',
        'face_selector_order': 'best-worst',
        'face_selector_gender': 'female',
        'face_selector_race': 'white',
        'face_selector_age_start': 20,
        'face_selector_age_end': 40
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is True


def test_validate_invalid_face_selector_mode() -> None:
    """Test validation fails for invalid face selector mode."""
    settings = {
        'face_selector_mode': 'invalid_mode'
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('face_selector_mode' in err for err in result.errors)


def test_validate_invalid_face_selector_age() -> None:
    """Test validation fails for invalid age range."""
    settings = {
        'face_selector_age_start': -1
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('face_selector_age_start' in err for err in result.errors)


def test_validate_output_settings() -> None:
    """Test validation of output settings."""
    settings = {
        'output_image_quality': 80,
        'output_video_encoder': 'libx264',
        'output_video_preset': 'medium',
        'output_video_quality': 80,
        'temp_frame_format': 'jpg'
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is True


def test_validate_invalid_output_quality() -> None:
    """Test validation fails for out-of-range quality."""
    settings = {
        'output_image_quality': 101
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is False
    assert any('output_image_quality' in err for err in result.errors)


def test_validate_complex_settings() -> None:
    """Test validation of complex settings profile."""
    settings = {
        'processors': ['face_swapper', 'face_enhancer'],
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
        'execution_providers': ['cpu'],
        'execution_thread_count': 4,
        'output_video_encoder': 'libx264',
        'output_video_quality': 80,
        'temp_frame_format': 'jpg'
    }

    result = ProfileValidator.validate_settings(settings)
    assert result.valid is True
    assert len(result.errors) == 0
