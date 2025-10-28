"""
Settings manager for FaceFusion configuration profiles.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from facefusion_repository.settings.validator import SettingsValidator
from facefusion_repository.types import ValidationResult


class SettingsManager:
    """Manages FaceFusion settings profiles."""

    def __init__(self, settings_path: Optional[str] = None) -> None:
        """
        Initialize settings manager.

        Args:
            settings_path: Path to settings directory. If None, uses default.
        """
        if settings_path is None:
            settings_path = os.path.expanduser('~/.facefusion_repository/settings')

        self.settings_path = Path(settings_path)
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure settings directory exists."""
        self.settings_path.mkdir(parents=True, exist_ok=True)

    def _get_profile_path(self, name: str) -> Path:
        """
        Get path to profile file.

        Args:
            name: Profile name

        Returns:
            Path to profile file
        """
        # Sanitize profile name for filesystem
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        return self.settings_path / f'{safe_name}.json'

    def create_profile(
        self,
        name: str,
        settings: Dict[str, Any],
        description: Optional[str] = None,
        validate: bool = True
    ) -> bool:
        """
        Create new settings profile.

        Args:
            name: Profile name
            settings: Settings dictionary
            description: Optional description
            validate: Whether to validate settings

        Returns:
            True if creation successful
        """
        # Validate settings if requested
        if validate:
            validation_result = SettingsValidator.validate_settings(settings)
            if not validation_result.valid:
                print(f'Settings validation failed: {validation_result.errors}')
                return False
            if validation_result.warnings:
                print(f'Settings warnings: {validation_result.warnings}')

        profile_path = self._get_profile_path(name)

        # Check if profile already exists
        if profile_path.exists():
            print(f'Settings profile already exists: {name}')
            return False

        try:
            profile_data = {
                'name': name,
                'description': description or '',
                'version': '1.0.0',
                'created_date': datetime.utcnow().isoformat() + 'Z',
                'last_modified': datetime.utcnow().isoformat() + 'Z',
                'settings': settings
            }

            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)

            print(f'Created settings profile: {name}')
            return True

        except Exception as e:
            print(f'Error creating settings profile: {e}')
            return False

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve settings profile.

        Args:
            name: Profile name

        Returns:
            Profile data or None if not found
        """
        profile_path = self._get_profile_path(name)

        if not profile_path.exists():
            return None

        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f'Error reading settings profile: {e}')
            return None

    def list_profiles(self) -> List[str]:
        """
        List all available profiles.

        Returns:
            List of profile names
        """
        profiles = []
        try:
            for file_path in self.settings_path.glob('*.json'):
                # Read profile to get actual name
                with open(file_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    profiles.append(profile_data.get('name', file_path.stem))
        except Exception as e:
            print(f'Error listing settings profiles: {e}')

        return sorted(profiles)

    def update_profile(
        self,
        name: str,
        settings: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        validate: bool = True
    ) -> bool:
        """
        Update existing settings profile.

        Args:
            name: Profile name
            settings: New settings dictionary (optional)
            description: New description (optional)
            validate: Whether to validate settings

        Returns:
            True if update successful
        """
        profile_data = self.get_profile(name)
        if profile_data is None:
            print(f'Settings profile not found: {name}')
            return False

        # Update fields
        if settings is not None:
            if validate:
                validation_result = SettingsValidator.validate_settings(settings)
                if not validation_result.valid:
                    print(f'Settings validation failed: {validation_result.errors}')
                    return False
            profile_data['settings'] = settings

        if description is not None:
            profile_data['description'] = description

        profile_data['last_modified'] = datetime.utcnow().isoformat() + 'Z'

        try:
            profile_path = self._get_profile_path(name)
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)
            return True
        except Exception as e:
            print(f'Error updating settings profile: {e}')
            return False

    def delete_profile(self, name: str) -> bool:
        """
        Delete settings profile.

        Args:
            name: Profile name

        Returns:
            True if deletion successful
        """
        profile_path = self._get_profile_path(name)

        if not profile_path.exists():
            print(f'Settings profile not found: {name}')
            return False

        try:
            profile_path.unlink()
            print(f'Deleted settings profile: {name}')
            return True
        except Exception as e:
            print(f'Error deleting settings profile: {e}')
            return False

    def export_profile(self, name: str, output_path: str) -> bool:
        """
        Export profile to file.

        Args:
            name: Profile name
            output_path: Output file path

        Returns:
            True if export successful
        """
        profile_data = self.get_profile(name)
        if profile_data is None:
            print(f'Settings profile not found: {name}')
            return False

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)
            print(f'Exported settings profile to: {output_path}')
            return True
        except Exception as e:
            print(f'Error exporting settings profile: {e}')
            return False

    def import_profile(self, input_path: str, name: Optional[str] = None) -> bool:
        """
        Import profile from file.

        Args:
            input_path: Input file path
            name: Optional new name (uses name from file if not provided)

        Returns:
            True if import successful
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)

            # Use provided name or name from file
            profile_name = name or profile_data.get('name', 'imported_profile')

            # Validate settings
            settings = profile_data.get('settings', {})
            validation_result = SettingsValidator.validate_settings(settings)
            if not validation_result.valid:
                print(f'Settings validation failed: {validation_result.errors}')
                return False

            # Create profile
            return self.create_profile(
                name=profile_name,
                settings=settings,
                description=profile_data.get('description', 'Imported profile'),
                validate=False  # Already validated
            )

        except Exception as e:
            print(f'Error importing settings profile: {e}')
            return False
