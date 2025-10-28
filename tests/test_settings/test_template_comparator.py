"""
Tests for FaceFusion Repository System - Settings Template and Comparator.
"""

import pytest

from facefusion_repository.settings.comparator import ProfileComparator
from facefusion_repository.settings.template import SettingsTemplate
from facefusion_repository.types import SettingsProfile


def test_get_default_face_swap() -> None:
    """Test getting default face swap template."""
    settings = SettingsTemplate.get_default_face_swap()

    assert 'processors' in settings
    assert 'face_swapper' in settings['processors']
    assert settings['face_detector_model'] == 'yoloface'
    assert settings['execution_providers'] == ['cpu']


def test_get_high_quality_swap() -> None:
    """Test getting high quality swap template."""
    settings = SettingsTemplate.get_high_quality_swap()

    assert 'face_swapper' in settings['processors']
    assert 'face_enhancer' in settings['processors']
    assert settings['output_video_quality'] == 95


def test_get_fast_preview() -> None:
    """Test getting fast preview template."""
    settings = SettingsTemplate.get_fast_preview()

    assert settings['face_detector_size'] == '320x320'
    assert settings['output_video_preset'] == 'ultrafast'
    assert settings['output_video_quality'] == 60


def test_get_gpu_accelerated() -> None:
    """Test getting GPU accelerated template."""
    settings = SettingsTemplate.get_gpu_accelerated()

    assert 'cuda' in settings['execution_providers']
    assert settings['output_video_encoder'] == 'h264_nvenc'
    assert 'video_memory_strategy' in settings


def test_get_multi_face_swap() -> None:
    """Test getting multi-face swap template."""
    settings = SettingsTemplate.get_multi_face_swap()

    assert settings['face_selector_mode'] == 'many'


def test_get_reference_face_swap() -> None:
    """Test getting reference face swap template."""
    settings = SettingsTemplate.get_reference_face_swap()

    assert settings['face_selector_mode'] == 'reference'
    assert 'reference_face_distance' in settings


def test_get_all_templates() -> None:
    """Test getting all templates."""
    templates = SettingsTemplate.get_all_templates()

    assert 'default_swap' in templates
    assert 'high_quality' in templates
    assert 'fast_preview' in templates
    assert 'gpu_accelerated' in templates
    assert 'multi_face' in templates
    assert 'reference_face' in templates

    # All templates should have required keys
    for name, template in templates.items():
        assert 'processors' in template
        assert 'face_detector_model' in template


def test_get_template_descriptions() -> None:
    """Test getting template descriptions."""
    descriptions = SettingsTemplate.get_template_descriptions()

    assert 'default_swap' in descriptions
    assert 'high_quality' in descriptions
    assert len(descriptions) == 6

    # All descriptions should be non-empty strings
    for desc in descriptions.values():
        assert isinstance(desc, str)
        assert len(desc) > 0


def test_compare_identical_profiles() -> None:
    """Test comparing identical profiles."""
    settings = {'key1': 'value1', 'key2': 'value2'}

    profile1 = SettingsProfile(
        name='profile1',
        description='Test',
        settings=settings,
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    profile2 = SettingsProfile(
        name='profile2',
        description='Test',
        settings=settings.copy(),
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    comparison = ProfileComparator.compare_profiles(profile1, profile2)

    assert comparison.identical is True
    assert len(comparison.different_settings) == 0
    assert len(comparison.only_in_profile1) == 0
    assert len(comparison.only_in_profile2) == 0
    assert len(comparison.common_settings) == 2


def test_compare_different_values() -> None:
    """Test comparing profiles with different values."""
    profile1 = SettingsProfile(
        name='profile1',
        description='Test',
        settings={'key1': 'value1', 'key2': 'value2'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    profile2 = SettingsProfile(
        name='profile2',
        description='Test',
        settings={'key1': 'value1', 'key2': 'different'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    comparison = ProfileComparator.compare_profiles(profile1, profile2)

    assert comparison.identical is False
    assert len(comparison.different_settings) == 1
    assert 'key2' in comparison.different_settings
    assert comparison.different_settings['key2'] == ('value2', 'different')
    assert len(comparison.common_settings) == 1


def test_compare_different_keys() -> None:
    """Test comparing profiles with different keys."""
    profile1 = SettingsProfile(
        name='profile1',
        description='Test',
        settings={'key1': 'value1', 'key2': 'value2'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    profile2 = SettingsProfile(
        name='profile2',
        description='Test',
        settings={'key1': 'value1', 'key3': 'value3'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    comparison = ProfileComparator.compare_profiles(profile1, profile2)

    assert comparison.identical is False
    assert 'key2' in comparison.only_in_profile1
    assert 'key3' in comparison.only_in_profile2
    assert len(comparison.common_settings) == 1


def test_format_comparison() -> None:
    """Test formatting comparison result."""
    profile1 = SettingsProfile(
        name='profile1',
        description='Test',
        settings={'key1': 'value1', 'key2': 'value2'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    profile2 = SettingsProfile(
        name='profile2',
        description='Test',
        settings={'key1': 'value1', 'key2': 'different'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    comparison = ProfileComparator.compare_profiles(profile1, profile2)
    formatted = ProfileComparator.format_comparison(comparison)

    assert isinstance(formatted, str)
    assert 'profile1' in formatted
    assert 'profile2' in formatted
    assert 'Different Settings' in formatted
    assert 'key2' in formatted


def test_format_identical_comparison() -> None:
    """Test formatting identical profiles."""
    settings = {'key1': 'value1'}

    profile1 = SettingsProfile(
        name='profile1',
        description='Test',
        settings=settings,
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    profile2 = SettingsProfile(
        name='profile2',
        description='Test',
        settings=settings.copy(),
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    comparison = ProfileComparator.compare_profiles(profile1, profile2)
    formatted = ProfileComparator.format_comparison(comparison)

    assert 'identical' in formatted.lower()


def test_get_differences_summary() -> None:
    """Test getting differences summary."""
    profile1 = SettingsProfile(
        name='profile1',
        description='Test',
        settings={'key1': 'value1', 'key2': 'value2', 'key3': 'value3'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    profile2 = SettingsProfile(
        name='profile2',
        description='Test',
        settings={'key1': 'value1', 'key2': 'different', 'key4': 'value4'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    comparison = ProfileComparator.compare_profiles(profile1, profile2)
    summary = ProfileComparator.get_differences_summary(comparison)

    assert summary['total_settings'] == 4
    assert summary['common_identical'] == 1
    assert summary['different_values'] == 1
    assert summary['only_in_profile1'] == 1
    assert summary['only_in_profile2'] == 1


def test_highlight_critical_differences() -> None:
    """Test highlighting critical differences."""
    profile1 = SettingsProfile(
        name='profile1',
        description='Test',
        settings={
            'processors': ['face_swapper'],
            'face_detector_model': 'yoloface',
            'face_mask_blur': 0.3
        },
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    profile2 = SettingsProfile(
        name='profile2',
        description='Test',
        settings={
            'processors': ['face_enhancer'],
            'face_detector_model': 'scrfd',
            'face_mask_blur': 0.5
        },
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    comparison = ProfileComparator.compare_profiles(profile1, profile2)
    critical = ProfileComparator.highlight_critical_differences(comparison)

    assert len(critical) == 2
    assert any('processors' in diff for diff in critical)
    assert any('face_detector_model' in diff for diff in critical)
    # face_mask_blur should not be in critical differences
    assert not any('face_mask_blur' in diff for diff in critical)


def test_highlight_critical_missing_settings() -> None:
    """Test highlighting critical missing settings."""
    profile1 = SettingsProfile(
        name='profile1',
        description='Test',
        settings={
            'processors': ['face_swapper'],
            'face_mask_blur': 0.3
        },
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    profile2 = SettingsProfile(
        name='profile2',
        description='Test',
        settings={
            'execution_providers': ['cuda'],
            'face_mask_blur': 0.3
        },
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z'
    )

    comparison = ProfileComparator.compare_profiles(profile1, profile2)
    critical = ProfileComparator.highlight_critical_differences(comparison)

    assert len(critical) == 2
    assert any('processors' in diff for diff in critical)
    assert any('execution_providers' in diff for diff in critical)
