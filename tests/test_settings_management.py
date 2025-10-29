"""Tests for settings management functionality."""

import json
import tempfile
from pathlib import Path

import pytest

from facefusion_repository.settings import SettingsManager


@pytest.fixture
def temp_repository_path():
	"""Create a temporary repository path."""
	with tempfile.TemporaryDirectory() as temp_dir:
		yield temp_dir


def test_settings_manager_initialization(temp_repository_path):
	"""Test settings manager initialization."""
	manager = SettingsManager(temp_repository_path)
	assert manager is not None
	assert manager.settings_dir.exists()
	assert manager.settings_file.exists()


def test_builtin_templates_created(temp_repository_path):
	"""Test that built-in templates are created on initialization."""
	manager = SettingsManager(temp_repository_path)
	templates = manager.get_builtin_templates()
	
	assert 'high_quality' in templates
	assert 'fast_processing' in templates
	assert 'gpu_optimized' in templates
	
	# Verify templates exist in profiles
	profiles = manager.list_profiles()
	assert 'high_quality' in profiles
	assert 'fast_processing' in profiles
	assert 'gpu_optimized' in profiles


def test_create_profile(temp_repository_path):
	"""Test creating a new profile."""
	manager = SettingsManager(temp_repository_path)
	
	settings = {
		'face_detector_model': 'retinaface',
		'quality_threshold': 0.8
	}
	
	result = manager.create_profile('custom_profile', settings, 'Custom settings')
	assert result is True
	
	# Verify profile was created
	profiles = manager.list_profiles()
	assert 'custom_profile' in profiles


def test_create_duplicate_profile(temp_repository_path):
	"""Test that creating duplicate profile fails."""
	manager = SettingsManager(temp_repository_path)
	
	settings = {'test': 'value'}
	
	result1 = manager.create_profile('test_profile', settings)
	assert result1 is True
	
	result2 = manager.create_profile('test_profile', settings)
	assert result2 is False


def test_get_profile(temp_repository_path):
	"""Test getting a profile."""
	manager = SettingsManager(temp_repository_path)
	
	settings = {
		'face_detector_model': 'retinaface',
		'quality_threshold': 0.8
	}
	description = 'Test profile'
	
	manager.create_profile('test_profile', settings, description)
	
	profile = manager.get_profile('test_profile')
	assert profile is not None
	assert profile['description'] == description
	assert profile['settings'] == settings


def test_get_nonexistent_profile(temp_repository_path):
	"""Test getting a non-existent profile."""
	manager = SettingsManager(temp_repository_path)
	profile = manager.get_profile('nonexistent')
	assert profile is None


def test_update_profile(temp_repository_path):
	"""Test updating a profile."""
	manager = SettingsManager(temp_repository_path)
	
	original_settings = {'test': 'original'}
	manager.create_profile('test_profile', original_settings)
	
	new_settings = {'test': 'updated', 'new_field': 'value'}
	new_description = 'Updated description'
	
	result = manager.update_profile('test_profile', new_settings, new_description)
	assert result is True
	
	profile = manager.get_profile('test_profile')
	assert profile['settings'] == new_settings
	assert profile['description'] == new_description


def test_update_nonexistent_profile(temp_repository_path):
	"""Test that updating non-existent profile fails."""
	manager = SettingsManager(temp_repository_path)
	
	result = manager.update_profile('nonexistent', {'test': 'value'})
	assert result is False


def test_list_profiles(temp_repository_path):
	"""Test listing all profiles."""
	manager = SettingsManager(temp_repository_path)
	
	# Create some profiles
	manager.create_profile('profile1', {'test': '1'})
	manager.create_profile('profile2', {'test': '2'})
	
	profiles = manager.list_profiles()
	
	# Should include built-in templates plus custom profiles
	assert 'profile1' in profiles
	assert 'profile2' in profiles
	assert 'high_quality' in profiles


def test_delete_profile(temp_repository_path):
	"""Test deleting a profile."""
	manager = SettingsManager(temp_repository_path)
	
	manager.create_profile('test_profile', {'test': 'value'})
	
	result = manager.delete_profile('test_profile')
	assert result is True
	
	# Verify profile was deleted
	profiles = manager.list_profiles()
	assert 'test_profile' not in profiles


def test_delete_nonexistent_profile(temp_repository_path):
	"""Test that deleting non-existent profile fails."""
	manager = SettingsManager(temp_repository_path)
	
	result = manager.delete_profile('nonexistent')
	assert result is False


def test_apply_profile(temp_repository_path):
	"""Test applying a profile."""
	manager = SettingsManager(temp_repository_path)
	
	settings = {
		'face_detector_model': 'retinaface',
		'quality_threshold': 0.8
	}
	
	manager.create_profile('test_profile', settings)
	
	applied_settings = manager.apply_profile('test_profile')
	assert applied_settings == settings


def test_apply_nonexistent_profile(temp_repository_path):
	"""Test that applying non-existent profile returns None."""
	manager = SettingsManager(temp_repository_path)
	
	applied_settings = manager.apply_profile('nonexistent')
	assert applied_settings is None


def test_export_profile(temp_repository_path):
	"""Test exporting a profile."""
	manager = SettingsManager(temp_repository_path)
	
	settings = {
		'face_detector_model': 'retinaface',
		'quality_threshold': 0.8
	}
	description = 'Test profile'
	
	manager.create_profile('test_profile', settings, description)
	
	export_path = Path(temp_repository_path) / 'exported_profile.json'
	result = manager.export_profile('test_profile', str(export_path))
	
	assert result is True
	assert export_path.exists()
	
	# Verify exported content
	with open(export_path, 'r') as f:
		exported_data = json.load(f)
	
	assert exported_data['settings'] == settings
	assert exported_data['description'] == description


def test_export_nonexistent_profile(temp_repository_path):
	"""Test that exporting non-existent profile fails."""
	manager = SettingsManager(temp_repository_path)
	
	export_path = Path(temp_repository_path) / 'exported_profile.json'
	result = manager.export_profile('nonexistent', str(export_path))
	
	assert result is False


def test_import_profile(temp_repository_path):
	"""Test importing a profile."""
	manager = SettingsManager(temp_repository_path)
	
	# Create a profile JSON file
	settings = {
		'face_detector_model': 'retinaface',
		'quality_threshold': 0.8
	}
	description = 'Imported profile'
	
	profile_data = {
		'settings': settings,
		'description': description
	}
	
	import_path = Path(temp_repository_path) / 'import_profile.json'
	with open(import_path, 'w') as f:
		json.dump(profile_data, f)
	
	result = manager.import_profile('imported_profile', str(import_path))
	
	assert result is True
	
	# Verify profile was imported
	profile = manager.get_profile('imported_profile')
	assert profile is not None
	assert profile['settings'] == settings
	assert profile['description'] == description


def test_import_invalid_file(temp_repository_path):
	"""Test that importing invalid file fails."""
	manager = SettingsManager(temp_repository_path)
	
	result = manager.import_profile('test_profile', 'nonexistent_file.json')
	assert result is False


def test_builtin_template_content(temp_repository_path):
	"""Test that built-in templates have expected content."""
	manager = SettingsManager(temp_repository_path)
	
	# Check high_quality template
	high_quality = manager.get_profile('high_quality')
	assert high_quality is not None
	assert 'settings' in high_quality
	assert 'face_detector_model' in high_quality['settings']
	assert 'quality_threshold' in high_quality['settings']
	
	# Check fast_processing template
	fast_processing = manager.get_profile('fast_processing')
	assert fast_processing is not None
	assert 'settings' in fast_processing
	
	# Check gpu_optimized template
	gpu_optimized = manager.get_profile('gpu_optimized')
	assert gpu_optimized is not None
	assert 'settings' in gpu_optimized
