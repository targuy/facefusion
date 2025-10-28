"""
Preset collection for grouping related presets.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from facefusion_repository.presets.manager import PresetManager


class PresetCollection:
    """Manages collections of related presets."""

    def __init__(
        self,
        collections_path: Optional[str] = None,
        preset_manager: Optional[PresetManager] = None
    ) -> None:
        """
        Initialize collection manager.

        Args:
            collections_path: Path to collections file
            preset_manager: Preset manager instance
        """
        if collections_path is None:
            import os
            collections_path = os.path.expanduser('~/.facefusion_repository/collections.json')

        self.collections_file = Path(collections_path)
        self.preset_manager = preset_manager or PresetManager()

        self._collections: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

        # Ensure parent directory exists
        self.collections_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_collections(self) -> bool:
        """Load collections from disk."""
        if self._loaded:
            return True

        if not self.collections_file.exists():
            self._initialize_collections_file()

        try:
            with open(self.collections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._collections = data.get('collections', {})
            self._loaded = True
            return True
        except Exception as e:
            print(f'Error loading collections: {e}')
            return False

    def _save_collections(self) -> bool:
        """Save collections to disk."""
        try:
            data = {
                'version': '1.0.0',
                'last_modified': datetime.utcnow().isoformat() + 'Z',
                'collections': self._collections
            }
            with open(self.collections_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f'Error saving collections: {e}')
            return False

    def _initialize_collections_file(self) -> None:
        """Initialize empty collections file."""
        data = {
            'version': '1.0.0',
            'created_date': datetime.utcnow().isoformat() + 'Z',
            'last_modified': datetime.utcnow().isoformat() + 'Z',
            'collections': {}
        }
        with open(self.collections_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def create_collection(
        self,
        name: str,
        preset_names: List[str],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Create new preset collection.

        Args:
            name: Collection name
            preset_names: List of preset names
            description: Optional description
            tags: Optional tags

        Returns:
            True if creation successful
        """
        if not self._load_collections():
            return False

        if name in self._collections:
            print(f'Collection already exists: {name}')
            return False

        # Verify all presets exist
        for preset_name in preset_names:
            if self.preset_manager.get_preset(preset_name) is None:
                print(f'Preset not found: {preset_name}')
                return False

        try:
            self._collections[name] = {
                'name': name,
                'description': description or '',
                'presets': preset_names,
                'tags': tags or [],
                'created_date': datetime.utcnow().isoformat() + 'Z'
            }

            if self._save_collections():
                print(f'Created collection: {name}')
                return True
            return False

        except Exception as e:
            print(f'Error creating collection: {e}')
            return False

    def get_collection(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get collection by name.

        Args:
            name: Collection name

        Returns:
            Collection data or None
        """
        if not self._load_collections():
            return None
        return self._collections.get(name)

    def list_collections(self) -> List[str]:
        """
        List all collection names.

        Returns:
            List of collection names
        """
        if not self._load_collections():
            return []
        return sorted(self._collections.keys())

    def add_preset_to_collection(self, collection_name: str, preset_name: str) -> bool:
        """
        Add preset to existing collection.

        Args:
            collection_name: Collection name
            preset_name: Preset name to add

        Returns:
            True if successful
        """
        if not self._load_collections():
            return False

        if collection_name not in self._collections:
            print(f'Collection not found: {collection_name}')
            return False

        if self.preset_manager.get_preset(preset_name) is None:
            print(f'Preset not found: {preset_name}')
            return False

        collection = self._collections[collection_name]
        if preset_name in collection['presets']:
            print(f'Preset already in collection: {preset_name}')
            return False

        collection['presets'].append(preset_name)
        return self._save_collections()

    def remove_preset_from_collection(self, collection_name: str, preset_name: str) -> bool:
        """
        Remove preset from collection.

        Args:
            collection_name: Collection name
            preset_name: Preset name to remove

        Returns:
            True if successful
        """
        if not self._load_collections():
            return False

        if collection_name not in self._collections:
            print(f'Collection not found: {collection_name}')
            return False

        collection = self._collections[collection_name]
        if preset_name not in collection['presets']:
            print(f'Preset not in collection: {preset_name}')
            return False

        collection['presets'].remove(preset_name)
        return self._save_collections()

    def delete_collection(self, name: str) -> bool:
        """
        Delete collection.

        Args:
            name: Collection name

        Returns:
            True if deletion successful
        """
        if not self._load_collections():
            return False

        if name not in self._collections:
            print(f'Collection not found: {name}')
            return False

        del self._collections[name]
        if self._save_collections():
            print(f'Deleted collection: {name}')
            return True
        return False

    def export_collection(self, name: str, output_path: str) -> bool:
        """
        Export collection to JSON file.

        Args:
            name: Collection name
            output_path: Output file path

        Returns:
            True if export successful
        """
        collection = self.get_collection(name)
        if collection is None:
            print(f'Collection not found: {name}')
            return False

        try:
            # Include full preset data
            collection_data = collection.copy()
            collection_data['presets_data'] = []

            for preset_name in collection['presets']:
                preset = self.preset_manager.get_preset(preset_name)
                if preset:
                    collection_data['presets_data'].append(preset.to_dict())

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(collection_data, f, indent=2)

            print(f'Exported collection to: {output_path}')
            return True

        except Exception as e:
            print(f'Error exporting collection: {e}')
            return False
