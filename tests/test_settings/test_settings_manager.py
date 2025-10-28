"""
Tests for Settings Manager.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from facefusion_repository.settings.manager import SettingsManager


class TestSettingsManager(unittest.TestCase):
    """Test cases for SettingsManager."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_path = os.path.join(self.temp_dir, 'settings')
        self.manager = SettingsManager(self.settings_path)

    def tearDown(self) -> None:
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_profile(self) -> None:
        """Test creating a settings profile."""
        settings = {
            'processors': ['face_swapper'],
            'face_detector_model': 'yolo_face'
        }

        result = self.manager.create_profile(
            name='test_profile',
            settings=settings,
            description='Test profile'
        )

        self.assertTrue(result)
        profile = self.manager.get_profile('test_profile')
        self.assertIsNotNone(profile)
        self.assertEqual(profile['name'], 'test_profile')
        self.assertEqual(profile['settings'], settings)

    def test_create_duplicate_profile(self) -> None:
        """Test that duplicate profiles are rejected."""
        settings = {'processors': ['face_swapper']}

        self.manager.create_profile('test', settings)
        result = self.manager.create_profile('test', settings)

        self.assertFalse(result)

    def test_list_profiles(self) -> None:
        """Test listing profiles."""
        settings1 = {'processors': ['face_swapper']}
        settings2 = {'processors': ['face_enhancer']}

        self.manager.create_profile('profile1', settings1)
        self.manager.create_profile('profile2', settings2)

        profiles = self.manager.list_profiles()
        self.assertEqual(len(profiles), 2)
        self.assertIn('profile1', profiles)
        self.assertIn('profile2', profiles)

    def test_get_nonexistent_profile(self) -> None:
        """Test getting a profile that doesn't exist."""
        profile = self.manager.get_profile('nonexistent')
        self.assertIsNone(profile)

    def test_update_profile(self) -> None:
        """Test updating a profile."""
        settings = {'processors': ['face_swapper']}
        self.manager.create_profile('test', settings)

        new_settings = {'processors': ['face_enhancer']}
        result = self.manager.update_profile('test', settings=new_settings)

        self.assertTrue(result)
        profile = self.manager.get_profile('test')
        self.assertEqual(profile['settings'], new_settings)

    def test_delete_profile(self) -> None:
        """Test deleting a profile."""
        settings = {'processors': ['face_swapper']}
        self.manager.create_profile('test', settings)

        result = self.manager.delete_profile('test')
        self.assertTrue(result)

        profile = self.manager.get_profile('test')
        self.assertIsNone(profile)

    def test_export_import_profile(self) -> None:
        """Test exporting and importing a profile."""
        settings = {'processors': ['face_swapper'], 'face_detector_model': 'yolo_face'}
        self.manager.create_profile('test', settings, description='Test profile')

        export_path = os.path.join(self.temp_dir, 'export.json')
        result = self.manager.export_profile('test', export_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))

        # Delete original and import
        self.manager.delete_profile('test')
        result = self.manager.import_profile(export_path, 'imported')
        self.assertTrue(result)

        imported = self.manager.get_profile('imported')
        self.assertIsNotNone(imported)
        self.assertEqual(imported['settings'], settings)

    def test_invalid_settings(self) -> None:
        """Test that invalid settings are rejected."""
        settings = {
            'processors': ['invalid_processor'],
            'face_detector_model': 'invalid_model'
        }

        result = self.manager.create_profile('test', settings, validate=True)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
