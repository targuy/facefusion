"""
Character manager for grouping faces by person/character.

Manages character collections with full CRUD operations and face associations.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.types import Character, FaceEntry


class CharacterManager:
    """Manages character/person collections with associated faces."""
    
    def __init__(self, repository_path: Optional[str] = None) -> None:
        """
        Initialize character manager.
        
        Args:
            repository_path: Path to repository directory. If None, uses default.
        """
        if repository_path is None:
            repository_path = Path.home() / '.facefusion_repository'
        
        self.repository_path = Path(repository_path)
        self.characters_file = self.repository_path / 'characters.json'
        
        self._characters: Dict[str, Character] = {}
        self._loaded = False
    
    def initialize(self) -> bool:
        """
        Initialize character storage.
        
        Returns:
            True if initialization successful
        """
        try:
            self.repository_path.mkdir(parents=True, exist_ok=True)
            
            if not self.characters_file.exists():
                characters_data = {
                    'version': '1.0.0',
                    'created_date': datetime.utcnow().isoformat() + 'Z',
                    'last_modified': datetime.utcnow().isoformat() + 'Z',
                    'characters': []
                }
                with open(self.characters_file, 'w', encoding='utf-8') as f:
                    json.dump(characters_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f'Error initializing character manager: {e}')
            return False
    
    def _load_characters(self) -> bool:
        """Load characters from disk."""
        if self._loaded:
            return True
        
        if not self.characters_file.exists():
            return False
        
        try:
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._characters = {}
            for char_data in data.get('characters', []):
                character = Character.from_dict(char_data)
                self._characters[character.id] = character
            
            self._loaded = True
            return True
        except Exception as e:
            print(f'Error loading characters: {e}')
            return False
    
    def _save_characters(self) -> bool:
        """Save characters to disk."""
        try:
            # Preserve original created_date, update last_modified
            original_created = None
            if self.characters_file.exists():
                with open(self.characters_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    original_created = data.get('created_date')
            
            characters_data = {
                'version': '1.0.0',
                'created_date': original_created or datetime.utcnow().isoformat() + 'Z',
                'last_modified': datetime.utcnow().isoformat() + 'Z',
                'characters': [char.to_dict() for char in self._characters.values()]
            }
            
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f'Error saving characters: {e}')
            return False
    
    def add_character(
        self,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Character]:
        """
        Add a new character.
        
        Args:
            name: Character name
            description: Optional description
            tags: Optional tags
            
        Returns:
            Created Character object, or None if failed
        """
        self._load_characters()
        
        # Check if character name already exists
        for char in self._characters.values():
            if char.name == name:
                print(f'Character "{name}" already exists')
                return None
        
        try:
            character = Character(
                id=f'char_{uuid.uuid4().hex[:12]}',
                name=name,
                description=description,
                face_ids=[],
                created_date=datetime.utcnow().isoformat() + 'Z',
                tags=tags or []
            )
            
            self._characters[character.id] = character
            
            if self._save_characters():
                return character
            
            return None
        except Exception as e:
            print(f'Error adding character: {e}')
            return None
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Get character by ID."""
        self._load_characters()
        return self._characters.get(character_id)
    
    def get_character_by_name(self, name: str) -> Optional[Character]:
        """Get character by name."""
        self._load_characters()
        
        for character in self._characters.values():
            if character.name == name:
                return character
        
        return None
    
    def list_characters(self, tags: Optional[List[str]] = None) -> List[Character]:
        """
        List all characters, optionally filtered by tags.
        
        Args:
            tags: Optional tags to filter by
            
        Returns:
            List of Character objects
        """
        self._load_characters()
        
        characters = list(self._characters.values())
        
        # Filter by tags if provided
        if tags:
            characters = [
                char for char in characters
                if any(tag in char.tags for tag in tags)
            ]
        
        return characters
    
    def remove_character(self, character_id: str) -> bool:
        """
        Remove a character.
        
        Args:
            character_id: Character ID
            
        Returns:
            True if removed successfully
        """
        self._load_characters()
        
        if character_id not in self._characters:
            print(f'Character {character_id} not found')
            return False
        
        del self._characters[character_id]
        return self._save_characters()
    
    def update_character(
        self,
        character_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update character metadata.
        
        Args:
            character_id: Character ID
            name: New name (optional)
            description: New description (optional)
            tags: New tags (optional)
            
        Returns:
            True if updated successfully
        """
        self._load_characters()
        
        character = self._characters.get(character_id)
        if not character:
            print(f'Character {character_id} not found')
            return False
        
        if name is not None:
            character.name = name
        if description is not None:
            character.description = description
        if tags is not None:
            character.tags = tags
        
        return self._save_characters()
