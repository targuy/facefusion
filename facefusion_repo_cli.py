#!/usr/bin/env python3
"""
FaceFusion Repository CLI - Command-line interface for repository management.
"""

import sys
import argparse

from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.repository.character_manager import CharacterManager


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='FaceFusion Repository System - Manage faces with multi-axis orientation'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize repository')
    
    # Add character command
    parser_char_add = subparsers.add_parser('character-add', help='Add a character')
    parser_char_add.add_argument('--name', required=True, help='Character name')
    parser_char_add.add_argument('--description', help='Character description')
    parser_char_add.add_argument('--tags', help='Comma-separated tags')
    
    # List characters command
    parser_char_list = subparsers.add_parser('character-list', help='List characters')
    
    # Show character command
    parser_char_show = subparsers.add_parser('character-show', help='Show character details')
    parser_char_show.add_argument('--character-id', required=True, help='Character ID')
    
    # Remove character command
    parser_char_remove = subparsers.add_parser('character-remove', help='Remove character')
    parser_char_remove.add_argument('--character-id', required=True, help='Character ID')
    
    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show repository statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Execute commands
    try:
        if args.command == 'init':
            repo = RepositoryManager()
            if repo.initialize_repository():
                print('✓ Repository initialized successfully')
                return 0
            else:
                print('✗ Failed to initialize repository')
                return 1
        
        elif args.command == 'character-add':
            tags = [t.strip() for t in args.tags.split(',')]  if hasattr(args, 'tags') and args.tags else None
            char_mgr = CharacterManager()
            character = char_mgr.add_character(
                name=args.name,
                description=getattr(args, 'description', None),
                tags=tags
            )
            if character:
                print(f'✓ Character added: {character.id}')
                print(f'  Name: {character.name}')
                return 0
            else:
                print('✗ Failed to add character')
                return 1
        
        elif args.command == 'character-list':
            char_mgr = CharacterManager()
            characters = char_mgr.list_characters()
            if not characters:
                print('No characters found')
                return 0
            print(f'Found {len(characters)} character(s):')
            for char in characters:
                print(f'  {char.id}: {char.name}')
            return 0
        
        elif args.command == 'character-show':
            char_mgr = CharacterManager()
            character = char_mgr.get_character(args.character_id)
            if not character:
                print(f'✗ Character not found: {args.character_id}')
                return 1
            print('Character Details:')
            print(f'  ID: {character.id}')
            print(f'  Name: {character.name}')
            if character.description:
                print(f'  Description: {character.description}')
            return 0
        
        elif args.command == 'character-remove':
            char_mgr = CharacterManager()
            if char_mgr.remove_character(args.character_id):
                print(f'✓ Character removed: {args.character_id}')
                return 0
            else:
                print(f'✗ Failed to remove character')
                return 1
        
        elif args.command == 'stats':
            repo = RepositoryManager()
            stats = repo.get_statistics()
            print('Repository Statistics:')
            print(f'  Total Faces: {stats.total_faces}')
            print(f'  Average Quality: {stats.average_quality:.2f}')
            print(f'  Total Size: {stats.total_size_mb:.2f} MB')
            return 0
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
