"""
Preset manager for named face-settings combinations.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.presets.validator import PresetValidator
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.manager import SettingsManager
from facefusion_repository.types import Preset


class PresetManager:
    """Manages named presets combining faces and settings."""

    def __init__(
        self,
        presets_path: Optional[str] = None,
        repository_manager: Optional[RepositoryManager] = None,
        settings_manager: Optional[SettingsManager] = None
    ) -> None:
        """
        Initialize preset manager.

        Args:
            presets_path: Path to presets file. If None, uses default.
            repository_manager: Repository manager instance
            settings_manager: Settings manager instance
        """
        if presets_path is None:
            presets_path = os.path.expanduser('~/.facefusion_repository/presets.json')

        self.presets_file = Path(presets_path)
        self.repository_manager = repository_manager or RepositoryManager()
        self.settings_manager = settings_manager or SettingsManager()

        self._presets: Dict[str, Preset] = {}
        self._loaded = False

        # Ensure parent directory exists
        self.presets_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_presets(self) -> bool:
        """
        Load presets from disk.

        Returns:
            True if load successful
        """
        if self._loaded:
            return True

        if not self.presets_file.exists():
            self._initialize_presets_file()

        try:
            with open(self.presets_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._presets = {}
            for preset_data in data.get('presets', []):
                preset = Preset.from_dict(preset_data)
                self._presets[preset.name] = preset

            self._loaded = True
            return True

        except Exception as e:
            print(f'Error loading presets: {e}')
            return False

    def _save_presets(self) -> bool:
        """
        Save presets to disk.

        Returns:
            True if save successful
        """
        try:
            # Load current data to preserve metadata
            if self.presets_file.exists():
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    'version': '1.0.0',
                    'created_date': datetime.utcnow().isoformat() + 'Z'
                }

            # Update presets and modification time
            data['last_modified'] = datetime.utcnow().isoformat() + 'Z'
            data['presets'] = [preset.to_dict() for preset in self._presets.values()]

            # Write to file
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f'Error saving presets: {e}')
            return False

    def _initialize_presets_file(self) -> None:
        """Initialize empty presets file."""
        data = {
            'version': '1.0.0',
            'created_date': datetime.utcnow().isoformat() + 'Z',
            'last_modified': datetime.utcnow().isoformat() + 'Z',
            'presets': []
        }
        with open(self.presets_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def create_preset(
        self,
        name: str,
        face_id: str,
        settings_profile: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        validate: bool = True
    ) -> bool:
        """
        Create new preset.

        Args:
            name: Preset name
            face_id: Face ID from repository
            settings_profile: Settings profile name
            description: Optional description
            tags: Optional tags for categorization
            validate: Whether to validate references

        Returns:
            True if creation successful
        """
        # Load presets
        if not self._load_presets():
            return False

        # Check if preset already exists
        if name in self._presets:
            print(f'Preset already exists: {name}')
            return False

        # Validate if requested
        if validate:
            validator = PresetValidator(self.repository_manager, self.settings_manager)
            validation_result = validator.validate_preset(face_id, settings_profile)
            if not validation_result.valid:
                print(f'Preset validation failed: {validation_result.errors}')
                return False
            if validation_result.warnings:
                print(f'Preset warnings: {validation_result.warnings}')

        try:
            # Create preset
            preset = Preset(
                name=name,
                description=description or '',
                face_id=face_id,
                settings_profile=settings_profile,
                created_date=datetime.utcnow().isoformat() + 'Z',
                last_used=None,
                usage_count=0
            )

            # Add tags if provided (store in metadata)
            if tags:
                preset.tags = tags  # type: ignore

            self._presets[name] = preset

            # Save
            if not self._save_presets():
                return False

            print(f'Created preset: {name}')
            return True

        except Exception as e:
            print(f'Error creating preset: {e}')
            return False

    def get_preset(self, name: str) -> Optional[Preset]:
        """
        Retrieve preset by name.

        Args:
            name: Preset name

        Returns:
            Preset or None if not found
        """
        if not self._load_presets():
            return None

        return self._presets.get(name)

    def list_presets(
        self,
        filter_by_face_id: Optional[str] = None,
        filter_by_settings: Optional[str] = None
    ) -> List[Preset]:
        """
        List all presets with optional filters.

        Args:
            filter_by_face_id: Filter by specific face ID
            filter_by_settings: Filter by settings profile name

        Returns:
            List of Preset objects
        """
        if not self._load_presets():
            return []

        presets = list(self._presets.values())

        # Apply face ID filter
        if filter_by_face_id:
            presets = [p for p in presets if p.face_id == filter_by_face_id]

        # Apply settings filter
        if filter_by_settings:
            presets = [p for p in presets if p.settings_profile == filter_by_settings]

        return presets

    def update_preset(
        self,
        name: str,
        face_id: Optional[str] = None,
        settings_profile: Optional[str] = None,
        description: Optional[str] = None,
        validate: bool = True
    ) -> bool:
        """
        Update existing preset.

        Args:
            name: Preset name
            face_id: New face ID (optional)
            settings_profile: New settings profile (optional)
            description: New description (optional)
            validate: Whether to validate new references

        Returns:
            True if update successful
        """
        if not self._load_presets():
            return False

        if name not in self._presets:
            print(f'Preset not found: {name}')
            return False

        preset = self._presets[name]

        # Update fields
        if face_id is not None:
            if validate:
                validator = PresetValidator(self.repository_manager, self.settings_manager)
                validation_result = validator.validate_face_reference(face_id)
                if not validation_result.valid:
                    print(f'Face validation failed: {validation_result.errors}')
                    return False
            preset.face_id = face_id

        if settings_profile is not None:
            if validate:
                validator = PresetValidator(self.repository_manager, self.settings_manager)
                validation_result = validator.validate_settings_reference(settings_profile)
                if not validation_result.valid:
                    print(f'Settings validation failed: {validation_result.errors}')
                    return False
            preset.settings_profile = settings_profile

        if description is not None:
            preset.description = description

        # Save
        return self._save_presets()

    def delete_preset(self, name: str) -> bool:
        """
        Delete preset.

        Args:
            name: Preset name

        Returns:
            True if deletion successful
        """
        if not self._load_presets():
            return False

        if name not in self._presets:
            print(f'Preset not found: {name}')
            return False

        try:
            del self._presets[name]
            if self._save_presets():
                print(f'Deleted preset: {name}')
                return True
            return False

        except Exception as e:
            print(f'Error deleting preset: {e}')
            return False

    def copy_preset(
        self,
        source_name: str,
        new_name: str,
        **kwargs
    ) -> bool:
        """
        Copy preset with optional modifications.

        Args:
            source_name: Source preset name
            new_name: New preset name
            **kwargs: Optional overrides (face_id, settings_profile, description)

        Returns:
            True if copy successful
        """
        source_preset = self.get_preset(source_name)
        if source_preset is None:
            print(f'Source preset not found: {source_name}')
            return False

        # Get values from source or overrides
        face_id = kwargs.get('face_id', source_preset.face_id)
        settings_profile = kwargs.get('settings_profile', source_preset.settings_profile)
        description = kwargs.get('description', f'Copy of {source_preset.description}')

        return self.create_preset(
            name=new_name,
            face_id=face_id,
            settings_profile=settings_profile,
            description=description,
            validate=kwargs.get('validate', True)
        )

    def export_preset(self, name: str, output_path: str) -> bool:
        """
        Export preset to JSON file.

        Args:
            name: Preset name
            output_path: Output file path

        Returns:
            True if export successful
        """
        preset = self.get_preset(name)
        if preset is None:
            print(f'Preset not found: {name}')
            return False

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(preset.to_dict(), f, indent=2)
            print(f'Exported preset to: {output_path}')
            return True

        except Exception as e:
            print(f'Error exporting preset: {e}')
            return False

    def import_preset(self, input_path: str, name: Optional[str] = None) -> bool:
        """
        Import preset from JSON file.

        Args:
            input_path: Input file path
            name: Optional new name (uses name from file if not provided)

        Returns:
            True if import successful
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)

            # Use provided name or name from file
            preset_name = name or preset_data.get('name', 'imported_preset')

            return self.create_preset(
                name=preset_name,
                face_id=preset_data['face_id'],
                settings_profile=preset_data['settings_profile'],
                description=preset_data.get('description', 'Imported preset'),
                validate=True
            )

        except Exception as e:
            print(f'Error importing preset: {e}')
            return False

    def increment_usage(self, name: str) -> bool:
        """
        Increment usage counter for preset.

        Args:
            name: Preset name

        Returns:
            True if update successful
        """
        if not self._load_presets():
            return False

        if name not in self._presets:
            return False

        preset = self._presets[name]
        preset.usage_count += 1
        preset.last_used = datetime.utcnow().isoformat() + 'Z'

        return self._save_presets()
