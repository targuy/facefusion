"""
Tests for Settings Validator.
"""

import unittest

from facefusion_repository.settings.validator import SettingsValidator


class TestSettingsValidator(unittest.TestCase):
    """Test cases for SettingsValidator."""

    def test_valid_settings(self) -> None:
        """Test validation of valid settings."""
        settings = {
            'processors': ['face_swapper'],
            'face_detector_model': 'yolo_face',
            'face_detector_size': '640x640',
            'face_detector_score': 0.5,
            'face_selector_mode': 'one'
        }

        result = SettingsValidator.validate_settings(settings)
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)

    def test_invalid_processor(self) -> None:
        """Test validation with invalid processor."""
        settings = {
            'processors': ['invalid_processor']
        }

        result = SettingsValidator.validate_settings(settings)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)

    def test_invalid_detector_model(self) -> None:
        """Test validation with invalid detector model."""
        settings = {
            'face_detector_model': 'invalid_model'
        }

        result = SettingsValidator.validate_settings(settings)
        self.assertFalse(result.valid)
        self.assertIn('Invalid face_detector_model', result.errors[0])

    def test_invalid_detector_score(self) -> None:
        """Test validation with invalid detector score."""
        settings = {
            'face_detector_score': 1.5  # Invalid: should be 0.0-1.0
        }

        result = SettingsValidator.validate_settings(settings)
        self.assertFalse(result.valid)

    def test_invalid_mask_padding(self) -> None:
        """Test validation with invalid mask padding."""
        settings = {
            'face_mask_padding': [0, 0]  # Invalid: should have 4 values
        }

        result = SettingsValidator.validate_settings(settings)
        self.assertFalse(result.valid)

    def test_unknown_settings_warning(self) -> None:
        """Test that unknown settings generate warnings."""
        settings = {
            'processors': ['face_swapper'],
            'unknown_setting': 'value'
        }

        result = SettingsValidator.validate_settings(settings)
        self.assertTrue(result.valid)
        self.assertGreater(len(result.warnings), 0)

    def test_validate_processors(self) -> None:
        """Test processor validation."""
        self.assertTrue(SettingsValidator.validate_processors(['face_swapper']))
        self.assertTrue(SettingsValidator.validate_processors(['face_swapper', 'face_enhancer']))
        self.assertFalse(SettingsValidator.validate_processors(['invalid']))
        self.assertFalse(SettingsValidator.validate_processors('not_a_list'))

    def test_validate_masker_types(self) -> None:
        """Test masker types validation."""
        self.assertTrue(SettingsValidator.validate_masker_types(['box']))
        self.assertTrue(SettingsValidator.validate_masker_types(['box', 'region']))
        self.assertFalse(SettingsValidator.validate_masker_types(['invalid']))
        self.assertFalse(SettingsValidator.validate_masker_types('not_a_list'))

    def test_get_available_options(self) -> None:
        """Test getting available options."""
        options = SettingsValidator.get_available_options()

        self.assertIn('processors', options)
        self.assertIn('face_detector_model', options)
        self.assertIsInstance(options['processors'], list)
        self.assertGreater(len(options['processors']), 0)


if __name__ == '__main__':
    unittest.main()
