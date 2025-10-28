"""
Settings manager for FaceFusion configuration profiles.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from facefusion_repository.types import SettingsProfile


class SettingsManager:
    """Manages FaceFusion settings profiles."""

    def __init__(self, settings_path: Optional[str] = None) -> None:
        """
        Initialize settings manager.

        Args:
            settings_path: Path to settings directory. If None, uses default.
        """
        if settings_path is None:
            repository_path = os.path.expanduser('~/.facefusion_repository')
            settings_path = os.path.join(repository_path, 'settings')

        self.settings_path = Path(settings_path)
        self._ensure_settings_directory()

    def _ensure_settings_directory(self) -> None:
        """Ensure settings directory exists."""
        self.settings_path.mkdir(parents=True, exist_ok=True)

    def _get_profile_path(self, name: str) -> Path:
        """
        Get path for a profile file.

        Args:
            name: Profile name

        Returns:
            Path to profile file
        """
        # Sanitize filename
        safe_name = name.replace('/', '_').replace('\\', '_')
        return self.settings_path / f'{safe_name}.json'

    def create_profile(
        self,
        name: str,
        settings: Dict[str, Any],
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Create new settings profile.

        Args:
            name: Profile name
            settings: FaceFusion settings dictionary
            description: Optional profile description
            tags: Optional tags for categorization

        Returns:
            True if creation successful
        """
        if not name:
            print('Error: Profile name cannot be empty')
            return False

        profile_path = self._get_profile_path(name)

        if profile_path.exists():
            print(f'Error: Profile "{name}" already exists')
            return False

        try:
            now = datetime.utcnow().isoformat() + 'Z'
            profile = SettingsProfile(
                name=name,
                description=description,
                settings=settings,
                created_date=now,
                modified_date=now,
                tags=tags or []
            )

            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2)

            print(f'✓ Profile "{name}" created successfully')
            return True

        except Exception as e:
            print(f'Error creating profile: {e}')
            return False

    def get_profile(self, name: str) -> Optional[SettingsProfile]:
        """
        Retrieve settings profile.

        Args:
            name: Profile name

        Returns:
            SettingsProfile or None if not found
        """
        profile_path = self._get_profile_path(name)

        if not profile_path.exists():
            return None

        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return SettingsProfile.from_dict(data)

        except Exception as e:
            print(f'Error loading profile: {e}')
            return None

    def list_profiles(
        self,
        filter_by_tags: Optional[List[str]] = None
    ) -> List[SettingsProfile]:
        """
        List all available profiles.

        Args:
            filter_by_tags: Filter by tags (profile must have all specified tags)

        Returns:
            List of SettingsProfile objects
        """
        profiles = []

        try:
            for profile_file in self.settings_path.glob('*.json'):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profile = SettingsProfile.from_dict(data)

                    # Apply tag filter
                    if filter_by_tags:
                        if not all(tag in profile.tags for tag in filter_by_tags):
                            continue

                    profiles.append(profile)

        except Exception as e:
            print(f'Error listing profiles: {e}')

        # Sort by name
        profiles.sort(key=lambda p: p.name)
        return profiles

    def update_profile(
        self,
        name: str,
        settings: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update existing settings profile.

        Args:
            name: Profile name
            settings: Optional new settings dictionary
            description: Optional new description
            tags: Optional new tags

        Returns:
            True if update successful
        """
        profile = self.get_profile(name)

        if not profile:
            print(f'Error: Profile "{name}" not found')
            return False

        try:
            # Update fields
            if settings is not None:
                profile.settings = settings
            if description is not None:
                profile.description = description
            if tags is not None:
                profile.tags = tags

            profile.modified_date = datetime.utcnow().isoformat() + 'Z'

            # Save updated profile
            profile_path = self._get_profile_path(name)
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2)

            print(f'✓ Profile "{name}" updated successfully')
            return True

        except Exception as e:
            print(f'Error updating profile: {e}')
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
            print(f'Error: Profile "{name}" not found')
            return False

        try:
            profile_path.unlink()
            print(f'✓ Profile "{name}" deleted successfully')
            return True

        except Exception as e:
            print(f'Error deleting profile: {e}')
            return False

    def export_profile(self, name: str, output_path: str) -> bool:
        """
        Export profile to file.

        Args:
            name: Profile name
            output_path: Path to export file

        Returns:
            True if export successful
        """
        profile = self.get_profile(name)

        if not profile:
            print(f'Error: Profile "{name}" not found')
            return False

        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2)

            print(f'✓ Profile "{name}" exported to {output_path}')
            return True

        except Exception as e:
            print(f'Error exporting profile: {e}')
            return False

    def import_profile(self, input_path: str, name: Optional[str] = None) -> bool:
        """
        Import profile from file.

        Args:
            input_path: Path to import file
            name: Optional new name for the profile (uses original if not provided)

        Returns:
            True if import successful
        """
        try:
            input_file = Path(input_path)

            if not input_file.exists():
                print(f'Error: File not found: {input_path}')
                return False

            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Use provided name or original name
            profile_name = name if name else data.get('name', 'imported_profile')

            # Check if profile already exists
            if self._get_profile_path(profile_name).exists():
                print(f'Error: Profile "{profile_name}" already exists')
                return False

            # Create profile with potentially new name
            profile = SettingsProfile.from_dict(data)
            profile.name = profile_name

            profile_path = self._get_profile_path(profile_name)
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2)

            print(f'✓ Profile "{profile_name}" imported successfully')
            return True

        except Exception as e:
            print(f'Error importing profile: {e}')
            return False
