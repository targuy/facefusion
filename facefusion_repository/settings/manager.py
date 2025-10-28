"""
Settings manager for FaceFusion parameter profiles.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.types import FaceFusionSettings, ValidationResult


class SettingsManager:
    """Manages FaceFusion settings profiles."""

    def __init__(self, repository_path: Optional[str] = None) -> None:
        """
        Initialize settings manager.

        Args:
            repository_path: Path to repository directory. If None, uses default.
        """
        if repository_path is None:
            repository_path = os.path.expanduser('~/.facefusion_repository')

        self.repository_path = Path(repository_path)
        self.settings_dir = self.repository_path / 'settings'
        self.settings_file = self.settings_dir / 'profiles.json'

        self._settings: Dict[str, FaceFusionSettings] = {}
        self._loaded = False

    def _load_settings(self) -> bool:
        """
        Load settings from disk.

        Returns:
            True if load successful
        """
        if self._loaded:
            return True

        if not self.settings_file.exists():
            return False

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._settings = {}
            for settings_data in data.get('profiles', []):
                settings = FaceFusionSettings.from_dict(settings_data)
                self._settings[settings.name] = settings

            self._loaded = True
            return True
        except Exception as e:
            print(f'Error loading settings: {e}')
            return False

    def _save_settings(self) -> bool:
        """
        Save settings to disk.

        Returns:
            True if save successful
        """
        try:
            self.settings_dir.mkdir(parents=True, exist_ok=True)

            data = {
                'version': '2.0.0',
                'last_modified': datetime.utcnow().isoformat() + 'Z',
                'profiles': [settings.to_dict() for settings in self._settings.values()]
            }

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f'Error saving settings: {e}')
            return False

    def create_settings(
        self,
        name: str,
        description: str,
        parameters: Dict[str, any],
        template: Optional[str] = None
    ) -> bool:
        """
        Create a new settings profile.

        Args:
            name: Settings profile name
            description: Description of the profile
            parameters: FaceFusion parameters dictionary
            template: Optional template to base settings on

        Returns:
            True if creation successful
        """
        self._load_settings()

        if name in self._settings:
            print(f'Settings profile "{name}" already exists.')
            return False

        # Apply template if specified
        if template:
            template_params = self._get_template_parameters(template)
            if template_params:
                # Merge template with user parameters (user parameters override)
                parameters = {**template_params, **parameters}

        try:
            settings = FaceFusionSettings(
                name=name,
                description=description,
                parameters=parameters,
                created_date=datetime.utcnow().isoformat() + 'Z',
                last_modified=datetime.utcnow().isoformat() + 'Z'
            )

            self._settings[name] = settings
            return self._save_settings()
        except Exception as e:
            print(f'Error creating settings: {e}')
            return False

    def get_settings(self, name: str) -> Optional[FaceFusionSettings]:
        """
        Get a settings profile by name.

        Args:
            name: Settings profile name

        Returns:
            FaceFusionSettings if found, None otherwise
        """
        self._load_settings()
        return self._settings.get(name)

    def list_settings(self) -> List[FaceFusionSettings]:
        """
        List all settings profiles.

        Returns:
            List of FaceFusionSettings objects
        """
        self._load_settings()
        return list(self._settings.values())

    def delete_settings(self, name: str) -> bool:
        """
        Delete a settings profile.

        Args:
            name: Settings profile name

        Returns:
            True if deletion successful
        """
        self._load_settings()

        if name not in self._settings:
            print(f'Settings profile "{name}" not found.')
            return False

        try:
            del self._settings[name]
            return self._save_settings()
        except Exception as e:
            print(f'Error deleting settings: {e}')
            return False

    def validate_settings(self, parameters: Dict[str, any]) -> ValidationResult:
        """
        Validate FaceFusion parameters.

        Args:
            parameters: Parameters to validate

        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []

        # Basic parameter validation
        known_params = {
            'face_detector_model', 'face_detector_score', 'face_detector_size',
            'face_landmarker_model', 'face_landmarker_score',
            'face_swapper_model', 'face_enhancer_model',
            'execution_providers', 'execution_device_ids',
            'output_video_encoder', 'output_video_quality'
        }

        for param in parameters:
            if param not in known_params:
                warnings.append(f'Unknown parameter: {param}')

        # Validate specific parameter types
        if 'face_detector_score' in parameters:
            score = parameters['face_detector_score']
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                errors.append('face_detector_score must be between 0 and 1')

        if 'execution_providers' in parameters:
            providers = parameters['execution_providers']
            if not isinstance(providers, list):
                errors.append('execution_providers must be a list')

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def _get_template_parameters(template: str) -> Optional[Dict[str, any]]:
        """
        Get parameters for a template.

        Args:
            template: Template name

        Returns:
            Parameters dictionary or None if template not found
        """
        templates = {
            'high_quality': {
                'face_detector_model': 'yolov8n',
                'face_detector_score': 0.7,
                'face_landmarker_model': '2dfan4',
                'face_swapper_model': 'inswapper_128',
                'face_enhancer_model': 'gfpgan_1.4',
                'output_video_quality': 95
            },
            'fast': {
                'face_detector_model': 'yolo_face',
                'face_detector_score': 0.5,
                'face_landmarker_model': '2dfan4',
                'face_swapper_model': 'inswapper_128',
                'output_video_quality': 85
            },
            'gpu_accelerated': {
                'face_detector_model': 'yolov8n',
                'face_detector_score': 0.6,
                'execution_providers': ['cuda'],
                'face_swapper_model': 'inswapper_128',
                'face_enhancer_model': 'gfpgan_1.4'
            },
            'cpu_optimized': {
                'face_detector_model': 'yolo_face',
                'face_detector_score': 0.5,
                'execution_providers': ['cpu'],
                'face_swapper_model': 'inswapper_128'
            }
        }

        return templates.get(template)

    @staticmethod
    def list_templates() -> List[str]:
        """
        List available settings templates.

        Returns:
            List of template names
        """
        return ['high_quality', 'fast', 'gpu_accelerated', 'cpu_optimized']
