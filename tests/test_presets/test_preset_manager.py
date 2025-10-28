"""
Tests for Preset Manager.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from facefusion_repository.presets.manager import PresetManager
from facefusion_repository.types import FaceEntry, FaceMetadata, QualityMetrics
import numpy


class TestPresetManager(unittest.TestCase):
    """Test cases for PresetManager."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.presets_file = os.path.join(self.temp_dir, 'presets.json')

        # Mock repository and settings managers
        self.mock_repo = MagicMock()
        self.mock_settings = MagicMock()

        # Create test face entry
        self.test_face = FaceEntry(
            id='test_face_001',
            file_path='/tmp/test.jpg',
            orientation_angle=0,
            quality_metrics=QualityMetrics(
                resolution=(512, 512),
                sharpness=0.8,
                detector_score=0.9,
                brightness=0.6,
                contrast=0.5,
                overall_quality=0.8
            ),
            face_embedding=numpy.zeros(512),
            face_landmarks={'5': [], '68': []},
            metadata=FaceMetadata(
                added_date=datetime.utcnow().isoformat() + 'Z',
                name='Test Face'
            )
        )

        # Configure mocks
        self.mock_repo.get_face.return_value = self.test_face
        self.mock_settings.get_profile.return_value = {
            'name': 'test_settings',
            'settings': {'processors': ['face_swapper']}
        }

        self.manager = PresetManager(
            presets_path=self.presets_file,
            repository_manager=self.mock_repo,
            settings_manager=self.mock_settings
        )

    def tearDown(self) -> None:
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_preset(self) -> None:
        """Test creating a preset."""
        result = self.manager.create_preset(
            name='test_preset',
            face_id='test_face_001',
            settings_profile='test_settings',
            description='Test preset',
            validate=False
        )

        self.assertTrue(result)
        preset = self.manager.get_preset('test_preset')
        self.assertIsNotNone(preset)
        self.assertEqual(preset.name, 'test_preset')
        self.assertEqual(preset.face_id, 'test_face_001')
        self.assertEqual(preset.settings_profile, 'test_settings')

    def test_create_duplicate_preset(self) -> None:
        """Test that duplicate presets are rejected."""
        self.manager.create_preset(
            name='test',
            face_id='face1',
            settings_profile='settings1',
            validate=False
        )

        result = self.manager.create_preset(
            name='test',
            face_id='face2',
            settings_profile='settings2',
            validate=False
        )

        self.assertFalse(result)

    def test_list_presets(self) -> None:
        """Test listing presets."""
        self.manager.create_preset('preset1', 'face1', 'settings1', validate=False)
        self.manager.create_preset('preset2', 'face2', 'settings2', validate=False)

        presets = self.manager.list_presets()
        self.assertEqual(len(presets), 2)

    def test_list_presets_with_filters(self) -> None:
        """Test listing presets with filters."""
        self.manager.create_preset('preset1', 'face1', 'settings1', validate=False)
        self.manager.create_preset('preset2', 'face1', 'settings2', validate=False)
        self.manager.create_preset('preset3', 'face2', 'settings1', validate=False)

        # Filter by face ID
        presets = self.manager.list_presets(filter_by_face_id='face1')
        self.assertEqual(len(presets), 2)

        # Filter by settings
        presets = self.manager.list_presets(filter_by_settings='settings1')
        self.assertEqual(len(presets), 2)

    def test_update_preset(self) -> None:
        """Test updating a preset."""
        self.manager.create_preset('test', 'face1', 'settings1', validate=False)

        result = self.manager.update_preset(
            'test',
            face_id='face2',
            validate=False
        )

        self.assertTrue(result)
        preset = self.manager.get_preset('test')
        self.assertEqual(preset.face_id, 'face2')

    def test_delete_preset(self) -> None:
        """Test deleting a preset."""
        self.manager.create_preset('test', 'face1', 'settings1', validate=False)

        result = self.manager.delete_preset('test')
        self.assertTrue(result)

        preset = self.manager.get_preset('test')
        self.assertIsNone(preset)

    def test_copy_preset(self) -> None:
        """Test copying a preset."""
        self.manager.create_preset(
            'original',
            'face1',
            'settings1',
            description='Original',
            validate=False
        )

        result = self.manager.copy_preset('original', 'copy', validate=False)
        self.assertTrue(result)

        copy = self.manager.get_preset('copy')
        self.assertIsNotNone(copy)
        self.assertEqual(copy.face_id, 'face1')
        self.assertEqual(copy.settings_profile, 'settings1')

    def test_copy_preset_with_overrides(self) -> None:
        """Test copying a preset with overrides."""
        self.manager.create_preset('original', 'face1', 'settings1', validate=False)

        result = self.manager.copy_preset(
            'original',
            'copy',
            face_id='face2',
            validate=False
        )

        self.assertTrue(result)
        copy = self.manager.get_preset('copy')
        self.assertEqual(copy.face_id, 'face2')

    def test_export_import_preset(self) -> None:
        """Test exporting and importing a preset."""
        self.manager.create_preset(
            'test',
            'face1',
            'settings1',
            description='Test',
            validate=False
        )

        export_path = os.path.join(self.temp_dir, 'preset.json')
        result = self.manager.export_preset('test', export_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))

        # Delete original and import
        self.manager.delete_preset('test')
        result = self.manager.import_preset(export_path, 'imported')
        self.assertTrue(result)

        imported = self.manager.get_preset('imported')
        self.assertIsNotNone(imported)

    def test_increment_usage(self) -> None:
        """Test incrementing usage counter."""
        self.manager.create_preset('test', 'face1', 'settings1', validate=False)

        preset = self.manager.get_preset('test')
        initial_count = preset.usage_count

        self.manager.increment_usage('test')

        preset = self.manager.get_preset('test')
        self.assertEqual(preset.usage_count, initial_count + 1)
        self.assertIsNotNone(preset.last_used)


if __name__ == '__main__':
    unittest.main()
