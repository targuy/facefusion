"""
Tests for Preset Validator.
"""

import os
import unittest
from unittest.mock import MagicMock

import numpy
from facefusion_repository.presets.validator import PresetValidator
from facefusion_repository.types import FaceEntry, FaceMetadata, QualityMetrics


class TestPresetValidator(unittest.TestCase):
    """Test cases for PresetValidator."""

    def setUp(self) -> None:
        """Set up test environment."""
        # Mock managers
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
                added_date='2025-10-28T00:00:00Z',
                name='Test Face'
            )
        )

        # Configure mocks
        self.mock_repo.get_face.return_value = self.test_face
        self.mock_settings.get_profile.return_value = {
            'name': 'test_settings',
            'settings': {
                'processors': ['face_swapper'],
                'face_detector_model': 'yolo_face'
            }
        }

        self.validator = PresetValidator(self.mock_repo, self.mock_settings)

    def test_validate_face_reference_valid(self) -> None:
        """Test validating a valid face reference."""
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            self.test_face.file_path = f.name

        result = self.validator.validate_face_reference('test_face_001')
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)

        # Cleanup
        os.unlink(self.test_face.file_path)

    def test_validate_face_reference_not_found(self) -> None:
        """Test validating non-existent face."""
        self.mock_repo.get_face.return_value = None

        result = self.validator.validate_face_reference('nonexistent')
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)

    def test_validate_face_reference_low_quality(self) -> None:
        """Test face with low quality generates warning."""
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            self.test_face.file_path = f.name
            self.test_face.quality_metrics.overall_quality = 0.3

        result = self.validator.validate_face_reference('test_face_001')
        self.assertTrue(result.valid)
        self.assertGreater(len(result.warnings), 0)

        # Cleanup
        os.unlink(self.test_face.file_path)

    def test_validate_settings_reference_valid(self) -> None:
        """Test validating valid settings reference."""
        result = self.validator.validate_settings_reference('test_settings')
        self.assertTrue(result.valid)

    def test_validate_settings_reference_not_found(self) -> None:
        """Test validating non-existent settings."""
        self.mock_settings.get_profile.return_value = None

        result = self.validator.validate_settings_reference('nonexistent')
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)

    def test_validate_preset_valid(self) -> None:
        """Test validating a complete valid preset."""
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            self.test_face.file_path = f.name

        result = self.validator.validate_preset('test_face_001', 'test_settings')
        self.assertTrue(result.valid)

        # Cleanup
        os.unlink(self.test_face.file_path)

    def test_validate_preset_invalid_face(self) -> None:
        """Test preset with invalid face."""
        self.mock_repo.get_face.return_value = None

        result = self.validator.validate_preset('invalid', 'test_settings')
        self.assertFalse(result.valid)

    def test_validate_compatibility(self) -> None:
        """Test face-settings compatibility validation."""
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            self.test_face.file_path = f.name

        result = self.validator.validate_compatibility('test_face_001', 'test_settings')
        self.assertTrue(result.valid)

        # Cleanup
        os.unlink(self.test_face.file_path)


if __name__ == '__main__':
    unittest.main()
