#!/usr/bin/env python3
"""
Standalone CLI for FaceFusion Repository System.

This provides a simple command-line interface to test and use the repository
system independently.
"""

import argparse
import sys

from facefusion import state_manager
from facefusion_repository.cli.commands import (
    cmd_repo_add_face,
    cmd_repo_add_person,
    cmd_repo_init,
    cmd_repo_list,
    cmd_repo_people,
    cmd_repo_remove,
    cmd_repo_show,
    cmd_repo_stats
)


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for repository CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='facefusion_repo',
        description='FaceFusion Repository System - Person-based face management with orientation matching',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # repo-init
    parser_init = subparsers.add_parser(
        'init',
        help='Initialize face repository'
    )

    # people (NEW)
    parser_people = subparsers.add_parser(
        'people',
        help='List all people in repository'
    )

    # add-person (NEW)
    parser_add_person = subparsers.add_parser(
        'add-person',
        help='Add a new person to repository'
    )
    parser_add_person.add_argument(
        '--person',
        required=True,
        help='Person identifier (alphanumeric, no spaces)'
    )
    parser_add_person.add_argument(
        '--display-name',
        help='Human-readable name (defaults to person id)'
    )

    # repo-add-face (UPDATED)
    parser_add = subparsers.add_parser(
        'add',
        help='Add face to repository for a person'
    )
    parser_add.add_argument(
        '--source',
        required=True,
        help='Path to face image'
    )
    parser_add.add_argument(
        '--person',
        required=True,
        help='Person this face belongs to'
    )
    parser_add.add_argument(
        '--name',
        help='Optional descriptive name for this specific face'
    )
    parser_add.add_argument(
        '--tags',
        help='Comma-separated tags'
    )

    # repo-list (UPDATED)
    parser_list = subparsers.add_parser(
        'list',
        help='List faces in repository'
    )
    parser_list.add_argument(
        '--person',
        help='Filter by person'
    )
    parser_list.add_argument(
        '--orientation',
        type=int,
        help='Filter by orientation angle'
    )
    parser_list.add_argument(
        '--tags',
        help='Filter by tags (comma-separated)'
    )

    # repo-show
    parser_show = subparsers.add_parser(
        'show',
        help='Show face details'
    )
    parser_show.add_argument(
        '--face-id',
        required=True,
        help='Face ID to show'
    )

    # repo-remove
    parser_remove = subparsers.add_parser(
        'remove',
        help='Remove face from repository'
    )
    parser_remove.add_argument(
        '--face-id',
        required=True,
        help='Face ID to remove'
    )

    # repo-stats
    parser_stats = subparsers.add_parser(
        'stats',
        help='Show repository statistics'
    )

    return parser


def main() -> int:
    """
    Main entry point for repository CLI.

    Returns:
        Exit code
    """
    # Initialize FaceFusion state manager with defaults
    state_manager.init_item('execution_device_ids', ['0'])
    state_manager.init_item('execution_providers', ['cpu'])
    state_manager.init_item('download_providers', ['github'])
    state_manager.init_item('face_detector_angles', [0])
    state_manager.init_item('face_detector_model', 'yolo_face')
    state_manager.init_item('face_detector_size', '640x640')
    state_manager.init_item('face_detector_score', 0.5)
    state_manager.init_item('face_landmarker_model', '2dfan4')
    state_manager.init_item('face_landmarker_score', 0.5)

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate command
    command_map = {
        'init': cmd_repo_init,
        'people': cmd_repo_people,
        'add-person': cmd_repo_add_person,
        'add': cmd_repo_add_face,
        'list': cmd_repo_list,
        'show': cmd_repo_show,
        'remove': cmd_repo_remove,
        'stats': cmd_repo_stats
    }

    command_func = command_map.get(args.command)
    if command_func:
        try:
            return command_func(args)
        except KeyboardInterrupt:
            print('\nOperation cancelled by user')
            return 130
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()
            return 1
    else:
        print(f'Unknown command: {args.command}')
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
