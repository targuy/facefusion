"""
Presets manager for person + settings combinations.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.types import Preset


class PresetsManager:
    """Manages presets combining person and settings."""

    def __init__(self, repository_path: Optional[str] = None) -> None:
        """
        Initialize presets manager.

        Args:
            repository_path: Path to repository directory. If None, uses default.
        """
        if repository_path is None:
            repository_path = os.path.expanduser('~/.facefusion_repository')

        self.repository_path = Path(repository_path)
        self.presets_dir = self.repository_path / 'presets'
        self.presets_file = self.presets_dir / 'presets.json'

        self._presets: Dict[str, Preset] = {}
        self._loaded = False

    def _load_presets(self) -> bool:
        """
        Load presets from disk.

        Returns:
            True if load successful
        """
        if self._loaded:
            return True

        if not self.presets_file.exists():
            return False

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
            self.presets_dir.mkdir(parents=True, exist_ok=True)

            data = {
                'version': '2.0.0',
                'last_modified': datetime.utcnow().isoformat() + 'Z',
                'presets': [preset.to_dict() for preset in self._presets.values()]
            }

            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f'Error saving presets: {e}')
            return False

    def create_preset(
        self,
        name: str,
        description: str,
        person_id: str,
        settings_name: str
    ) -> bool:
        """
        Create a new preset.

        Args:
            name: Preset name
            description: Description of the preset
            person_id: Person identifier
            settings_name: Settings profile name

        Returns:
            True if creation successful
        """
        self._load_presets()

        if name in self._presets:
            print(f'Preset "{name}" already exists.')
            return False

        try:
            preset = Preset(
                name=name,
                description=description,
                person_id=person_id,
                settings_name=settings_name,
                created_date=datetime.utcnow().isoformat() + 'Z'
            )

            self._presets[name] = preset
            return self._save_presets()
        except Exception as e:
            print(f'Error creating preset: {e}')
            return False

    def get_preset(self, name: str) -> Optional[Preset]:
        """
        Get a preset by name.

        Args:
            name: Preset name

        Returns:
            Preset if found, None otherwise
        """
        self._load_presets()
        return self._presets.get(name)

    def list_presets(self) -> List[Preset]:
        """
        List all presets.

        Returns:
            List of Preset objects
        """
        self._load_presets()
        return list(self._presets.values())

    def delete_preset(self, name: str) -> bool:
        """
        Delete a preset.

        Args:
            name: Preset name

        Returns:
            True if deletion successful
        """
        self._load_presets()

        if name not in self._presets:
            print(f'Preset "{name}" not found.')
            return False

        try:
            del self._presets[name]
            return self._save_presets()
        except Exception as e:
            print(f'Error deleting preset: {e}')
            return False

    def update_usage(self, name: str) -> bool:
        """
        Update usage statistics for a preset.

        Args:
            name: Preset name

        Returns:
            True if update successful
        """
        self._load_presets()

        preset = self._presets.get(name)
        if not preset:
            print(f'Preset "{name}" not found.')
            return False

        try:
            preset.usage_count += 1
            preset.last_used = datetime.utcnow().isoformat() + 'Z'
            return self._save_presets()
        except Exception as e:
            print(f'Error updating preset usage: {e}')
            return False
