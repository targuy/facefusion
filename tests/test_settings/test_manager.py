"""
Tests for FaceFusion Repository System - Settings Manager.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from facefusion_repository.settings.manager import SettingsManager
from facefusion_repository.types import SettingsProfile


@pytest.fixture
def temp_settings_dir() -> str:
    """Create temporary settings directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def settings_manager(temp_settings_dir: str) -> SettingsManager:
    """Create settings manager with temporary directory."""
    return SettingsManager(temp_settings_dir)


@pytest.fixture
def sample_settings() -> dict:
    """Create sample settings for testing."""
    return {
        'processors': ['face_swapper'],
        'face_detector_model': 'yoloface',
        'face_detector_size': '640x640',
        'face_detector_score': 0.5,
        'execution_providers': ['cpu']
    }


def test_create_profile(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test creating a new settings profile."""
    result = settings_manager.create_profile(
        name='test_profile',
        settings=sample_settings,
        description='Test profile',
        tags=['test', 'basic']
    )

    assert result is True

    # Verify profile was created
    profile = settings_manager.get_profile('test_profile')
    assert profile is not None
    assert profile.name == 'test_profile'
    assert profile.description == 'Test profile'
    assert profile.settings == sample_settings
    assert 'test' in profile.tags
    assert 'basic' in profile.tags


def test_create_profile_duplicate(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test creating duplicate profile fails."""
    settings_manager.create_profile('test_profile', sample_settings)

    # Try to create again
    result = settings_manager.create_profile('test_profile', sample_settings)
    assert result is False


def test_create_profile_empty_name(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test creating profile with empty name fails."""
    result = settings_manager.create_profile('', sample_settings)
    assert result is False


def test_get_profile(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test retrieving a profile."""
    settings_manager.create_profile('test_profile', sample_settings)

    profile = settings_manager.get_profile('test_profile')
    assert profile is not None
    assert profile.name == 'test_profile'
    assert profile.settings == sample_settings


def test_get_profile_not_found(settings_manager: SettingsManager) -> None:
    """Test retrieving non-existent profile returns None."""
    profile = settings_manager.get_profile('nonexistent')
    assert profile is None


def test_list_profiles(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test listing all profiles."""
    settings_manager.create_profile('profile1', sample_settings, tags=['tag1'])
    settings_manager.create_profile('profile2', sample_settings, tags=['tag2'])
    settings_manager.create_profile('profile3', sample_settings, tags=['tag1', 'tag2'])

    profiles = settings_manager.list_profiles()
    assert len(profiles) == 3

    # Test filtering by tags
    profiles = settings_manager.list_profiles(filter_by_tags=['tag1'])
    assert len(profiles) == 2

    profiles = settings_manager.list_profiles(filter_by_tags=['tag1', 'tag2'])
    assert len(profiles) == 1


def test_update_profile_settings(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test updating profile settings."""
    settings_manager.create_profile('test_profile', sample_settings)

    new_settings = {
        'processors': ['face_enhancer'],
        'face_detector_model': 'scrfd'
    }

    result = settings_manager.update_profile('test_profile', settings=new_settings)
    assert result is True

    profile = settings_manager.get_profile('test_profile')
    assert profile is not None
    assert profile.settings == new_settings


def test_update_profile_description(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test updating profile description."""
    settings_manager.create_profile('test_profile', sample_settings, description='Old description')

    result = settings_manager.update_profile('test_profile', description='New description')
    assert result is True

    profile = settings_manager.get_profile('test_profile')
    assert profile is not None
    assert profile.description == 'New description'


def test_update_profile_tags(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test updating profile tags."""
    settings_manager.create_profile('test_profile', sample_settings, tags=['old'])

    result = settings_manager.update_profile('test_profile', tags=['new', 'updated'])
    assert result is True

    profile = settings_manager.get_profile('test_profile')
    assert profile is not None
    assert 'new' in profile.tags
    assert 'updated' in profile.tags
    assert 'old' not in profile.tags


def test_update_profile_not_found(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test updating non-existent profile fails."""
    result = settings_manager.update_profile('nonexistent', settings=sample_settings)
    assert result is False


def test_delete_profile(settings_manager: SettingsManager, sample_settings: dict) -> None:
    """Test deleting a profile."""
    settings_manager.create_profile('test_profile', sample_settings)

    result = settings_manager.delete_profile('test_profile')
    assert result is True

    # Verify profile was deleted
    profile = settings_manager.get_profile('test_profile')
    assert profile is None


def test_delete_profile_not_found(settings_manager: SettingsManager) -> None:
    """Test deleting non-existent profile fails."""
    result = settings_manager.delete_profile('nonexistent')
    assert result is False


def test_export_profile(settings_manager: SettingsManager, sample_settings: dict, temp_settings_dir: str) -> None:
    """Test exporting a profile."""
    settings_manager.create_profile('test_profile', sample_settings, description='Export test')

    output_path = os.path.join(temp_settings_dir, 'exported_profile.json')
    result = settings_manager.export_profile('test_profile', output_path)
    assert result is True

    # Verify file was created
    assert os.path.exists(output_path)

    # Verify content
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data['name'] == 'test_profile'
    assert data['description'] == 'Export test'
    assert data['settings'] == sample_settings


def test_export_profile_not_found(settings_manager: SettingsManager, temp_settings_dir: str) -> None:
    """Test exporting non-existent profile fails."""
    output_path = os.path.join(temp_settings_dir, 'exported_profile.json')
    result = settings_manager.export_profile('nonexistent', output_path)
    assert result is False


def test_import_profile(settings_manager: SettingsManager, sample_settings: dict, temp_settings_dir: str) -> None:
    """Test importing a profile."""
    # Create profile file
    profile_data = {
        'name': 'imported_profile',
        'description': 'Imported test',
        'settings': sample_settings,
        'created_date': '2025-10-28T00:00:00Z',
        'modified_date': '2025-10-28T00:00:00Z',
        'version': '1.0.0',
        'tags': ['imported']
    }

    input_path = os.path.join(temp_settings_dir, 'import_profile.json')
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f)

    result = settings_manager.import_profile(input_path)
    assert result is True

    # Verify profile was imported
    profile = settings_manager.get_profile('imported_profile')
    assert profile is not None
    assert profile.name == 'imported_profile'
    assert profile.description == 'Imported test'
    assert profile.settings == sample_settings


def test_import_profile_with_new_name(settings_manager: SettingsManager, sample_settings: dict, temp_settings_dir: str) -> None:
    """Test importing a profile with a new name."""
    profile_data = {
        'name': 'original_name',
        'description': 'Test',
        'settings': sample_settings,
        'created_date': '2025-10-28T00:00:00Z',
        'modified_date': '2025-10-28T00:00:00Z',
        'version': '1.0.0',
        'tags': []
    }

    input_path = os.path.join(temp_settings_dir, 'import_profile.json')
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f)

    result = settings_manager.import_profile(input_path, name='new_name')
    assert result is True

    # Verify profile was imported with new name
    profile = settings_manager.get_profile('new_name')
    assert profile is not None
    assert profile.name == 'new_name'


def test_import_profile_file_not_found(settings_manager: SettingsManager) -> None:
    """Test importing from non-existent file fails."""
    result = settings_manager.import_profile('/nonexistent/path.json')
    assert result is False


def test_import_profile_duplicate(settings_manager: SettingsManager, sample_settings: dict, temp_settings_dir: str) -> None:
    """Test importing duplicate profile fails."""
    settings_manager.create_profile('test_profile', sample_settings)

    # Create profile file with same name
    profile_data = {
        'name': 'test_profile',
        'description': 'Test',
        'settings': sample_settings,
        'created_date': '2025-10-28T00:00:00Z',
        'modified_date': '2025-10-28T00:00:00Z',
        'version': '1.0.0',
        'tags': []
    }

    input_path = os.path.join(temp_settings_dir, 'import_profile.json')
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f)

    result = settings_manager.import_profile(input_path)
    assert result is False


def test_profile_serialization() -> None:
    """Test SettingsProfile serialization and deserialization."""
    profile = SettingsProfile(
        name='test',
        description='Test profile',
        settings={'key': 'value'},
        created_date='2025-10-28T00:00:00Z',
        modified_date='2025-10-28T00:00:00Z',
        version='1.0.0',
        tags=['tag1', 'tag2']
    )

    # Serialize
    data = profile.to_dict()
    assert data['name'] == 'test'
    assert data['description'] == 'Test profile'
    assert data['settings'] == {'key': 'value'}

    # Deserialize
    restored = SettingsProfile.from_dict(data)
    assert restored.name == profile.name
    assert restored.description == profile.description
    assert restored.settings == profile.settings
    assert restored.tags == profile.tags
