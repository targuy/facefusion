"""
Preset applicator for deploying configurations.
"""

from typing import Any, Dict, Optional

from facefusion_repository.presets.manager import PresetManager
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.manager import SettingsManager


class PresetApplicator:
    """Applies preset configurations for face swap operations."""

    def __init__(
        self,
        preset_manager: Optional[PresetManager] = None,
        repository_manager: Optional[RepositoryManager] = None,
        settings_manager: Optional[SettingsManager] = None
    ) -> None:
        """
        Initialize applicator.

        Args:
            preset_manager: Preset manager instance
            repository_manager: Repository manager instance
            settings_manager: Settings manager instance
        """
        self.preset_manager = preset_manager or PresetManager()
        self.repository_manager = repository_manager or RepositoryManager()
        self.settings_manager = settings_manager or SettingsManager()

    def get_preset_configuration(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete configuration from preset.

        Args:
            preset_name: Preset name

        Returns:
            Dictionary with face_path, settings, and metadata
        """
        # Get preset
        preset = self.preset_manager.get_preset(preset_name)
        if preset is None:
            print(f'Preset not found: {preset_name}')
            return None

        # Get face entry
        face_entry = self.repository_manager.get_face(preset.face_id)
        if face_entry is None:
            print(f'Face not found: {preset.face_id}')
            return None

        # Get settings profile
        profile = self.settings_manager.get_profile(preset.settings_profile)
        if profile is None:
            print(f'Settings profile not found: {preset.settings_profile}')
            return None

        # Build configuration
        return {
            'preset_name': preset_name,
            'face_path': face_entry.file_path,
            'face_id': preset.face_id,
            'settings': profile.get('settings', {}),
            'settings_profile': preset.settings_profile,
            'metadata': {
                'face_name': face_entry.metadata.name,
                'face_orientation': face_entry.orientation_angle,
                'face_quality': face_entry.quality_metrics.overall_quality,
                'preset_description': preset.description
            }
        }

    def apply_preset(
        self,
        preset_name: str,
        update_usage: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Apply preset and return configuration.

        Args:
            preset_name: Preset name
            update_usage: Whether to increment usage counter

        Returns:
            Configuration dictionary or None
        """
        config = self.get_preset_configuration(preset_name)
        if config is None:
            return None

        # Update usage statistics
        if update_usage:
            self.preset_manager.increment_usage(preset_name)

        return config

    def validate_preset_before_apply(self, preset_name: str) -> bool:
        """
        Validate preset before application.

        Args:
            preset_name: Preset name

        Returns:
            True if preset is valid and ready to apply
        """
        from facefusion_repository.presets.validator import PresetValidator

        preset = self.preset_manager.get_preset(preset_name)
        if preset is None:
            print(f'Preset not found: {preset_name}')
            return False

        validator = PresetValidator(self.repository_manager, self.settings_manager)
        result = validator.validate_preset(preset.face_id, preset.settings_profile)

        if not result.valid:
            print(f'Preset validation failed: {result.errors}')
            return False

        if result.warnings:
            print(f'Preset warnings: {result.warnings}')

        return True

    def get_face_path(self, preset_name: str) -> Optional[str]:
        """
        Get face file path from preset.

        Args:
            preset_name: Preset name

        Returns:
            Face file path or None
        """
        config = self.get_preset_configuration(preset_name)
        if config:
            return config['face_path']
        return None

    def get_settings(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get settings dictionary from preset.

        Args:
            preset_name: Preset name

        Returns:
            Settings dictionary or None
        """
        config = self.get_preset_configuration(preset_name)
        if config:
            return config['settings']
        return None

    def get_preset_summary(self, preset_name: str) -> Optional[str]:
        """
        Get human-readable summary of preset configuration.

        Args:
            preset_name: Preset name

        Returns:
            Summary string or None
        """
        config = self.get_preset_configuration(preset_name)
        if config is None:
            return None

        metadata = config['metadata']
        settings = config['settings']

        summary = f"""
Preset: {preset_name}
Description: {metadata['preset_description']}

Face Configuration:
  - Name: {metadata['face_name'] or 'Unnamed'}
  - Orientation: {metadata['face_orientation']}°
  - Quality: {metadata['face_quality']:.2f}
  - File: {config['face_path']}

Settings Profile: {config['settings_profile']}
  - Processors: {', '.join(settings.get('processors', []))}
  - Detector: {settings.get('face_detector_model', 'default')}
  - Detector Size: {settings.get('face_detector_size', 'default')}
  - Masker Types: {', '.join(settings.get('face_masker_types', []))}
"""
        return summary.strip()

    def compare_presets(self, preset1: str, preset2: str) -> Optional[Dict[str, Any]]:
        """
        Compare two presets.

        Args:
            preset1: First preset name
            preset2: Second preset name

        Returns:
            Comparison dictionary or None
        """
        config1 = self.get_preset_configuration(preset1)
        config2 = self.get_preset_configuration(preset2)

        if config1 is None or config2 is None:
            return None

        differences = {
            'same_face': config1['face_id'] == config2['face_id'],
            'same_settings': config1['settings_profile'] == config2['settings_profile'],
            'face_orientation_diff': abs(
                config1['metadata']['face_orientation'] -
                config2['metadata']['face_orientation']
            ),
            'quality_diff': abs(
                config1['metadata']['face_quality'] -
                config2['metadata']['face_quality']
            )
        }

        # Compare specific settings
        settings_diff = {}
        all_keys = set(config1['settings'].keys()) | set(config2['settings'].keys())
        for key in all_keys:
            val1 = config1['settings'].get(key)
            val2 = config2['settings'].get(key)
            if val1 != val2:
                settings_diff[key] = {'preset1': val1, 'preset2': val2}

        differences['settings_differences'] = settings_diff

        return differences
