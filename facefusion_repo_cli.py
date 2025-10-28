#!/usr/bin/env python3
"""
Standalone CLI for FaceFusion Repository System.

This provides a simple command-line interface to test and use the repository
system independently.
"""

import argparse
import sys

from facefusion_repository.cli.commands import (
    cmd_repo_add_face,
    cmd_repo_init,
    cmd_repo_list,
    cmd_repo_remove,
    cmd_repo_show,
    cmd_repo_stats,
    cmd_settings_compare,
    cmd_settings_create,
    cmd_settings_delete,
    cmd_settings_export,
    cmd_settings_import,
    cmd_settings_list,
    cmd_settings_show,
    cmd_settings_templates,
    cmd_settings_update,
    cmd_settings_validate
)

from facefusion import state_manager


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for repository CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='facefusion_repo',
        description='FaceFusion Repository System - Manage source faces with orientation-based matching',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # repo-init
    parser_init = subparsers.add_parser(
        'init',
        help='Initialize face repository'
    )

    # repo-add-face
    parser_add = subparsers.add_parser(
        'add',
        help='Add face to repository'
    )
    parser_add.add_argument(
        '--source',
        required=True,
        help='Path to face image'
    )
    parser_add.add_argument(
        '--name',
        help='Name for the face'
    )
    parser_add.add_argument(
        '--tags',
        help='Comma-separated tags'
    )

    # repo-list
    parser_list = subparsers.add_parser(
        'list',
        help='List faces in repository'
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

    # Settings commands
    # settings-create
    parser_settings_create = subparsers.add_parser(
        'settings-create',
        help='Create new settings profile'
    )
    parser_settings_create.add_argument(
        '--name',
        required=True,
        help='Profile name'
    )
    parser_settings_create.add_argument(
        '--template',
        help='Use predefined template (default_swap, high_quality, fast_preview, etc.)'
    )
    parser_settings_create.add_argument(
        '--settings-file',
        help='Path to JSON file with settings'
    )
    parser_settings_create.add_argument(
        '--description',
        help='Profile description'
    )
    parser_settings_create.add_argument(
        '--tags',
        help='Comma-separated tags'
    )

    # settings-list
    parser_settings_list = subparsers.add_parser(
        'settings-list',
        help='List settings profiles'
    )
    parser_settings_list.add_argument(
        '--tags',
        help='Filter by tags (comma-separated)'
    )

    # settings-show
    parser_settings_show = subparsers.add_parser(
        'settings-show',
        help='Show settings profile details'
    )
    parser_settings_show.add_argument(
        '--name',
        required=True,
        help='Profile name'
    )

    # settings-update
    parser_settings_update = subparsers.add_parser(
        'settings-update',
        help='Update settings profile'
    )
    parser_settings_update.add_argument(
        '--name',
        required=True,
        help='Profile name'
    )
    parser_settings_update.add_argument(
        '--settings-file',
        help='Path to JSON file with new settings'
    )
    parser_settings_update.add_argument(
        '--description',
        help='New description'
    )
    parser_settings_update.add_argument(
        '--tags',
        help='New tags (comma-separated)'
    )

    # settings-delete
    parser_settings_delete = subparsers.add_parser(
        'settings-delete',
        help='Delete settings profile'
    )
    parser_settings_delete.add_argument(
        '--name',
        required=True,
        help='Profile name'
    )

    # settings-compare
    parser_settings_compare = subparsers.add_parser(
        'settings-compare',
        help='Compare two settings profiles'
    )
    parser_settings_compare.add_argument(
        '--profile1',
        required=True,
        help='First profile name'
    )
    parser_settings_compare.add_argument(
        '--profile2',
        required=True,
        help='Second profile name'
    )

    # settings-export
    parser_settings_export = subparsers.add_parser(
        'settings-export',
        help='Export settings profile to file'
    )
    parser_settings_export.add_argument(
        '--name',
        required=True,
        help='Profile name'
    )
    parser_settings_export.add_argument(
        '--output',
        required=True,
        help='Output file path'
    )

    # settings-import
    parser_settings_import = subparsers.add_parser(
        'settings-import',
        help='Import settings profile from file'
    )
    parser_settings_import.add_argument(
        '--input',
        required=True,
        help='Input file path'
    )
    parser_settings_import.add_argument(
        '--name',
        help='Profile name (uses original if not provided)'
    )

    # settings-validate
    parser_settings_validate = subparsers.add_parser(
        'settings-validate',
        help='Validate settings profile'
    )
    parser_settings_validate.add_argument(
        '--name',
        required=True,
        help='Profile name'
    )

    # settings-templates
    parser_settings_templates = subparsers.add_parser(
        'settings-templates',
        help='List available settings templates'
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
        'add': cmd_repo_add_face,
        'list': cmd_repo_list,
        'show': cmd_repo_show,
        'remove': cmd_repo_remove,
        'stats': cmd_repo_stats,
        'settings-create': cmd_settings_create,
        'settings-list': cmd_settings_list,
        'settings-show': cmd_settings_show,
        'settings-update': cmd_settings_update,
        'settings-delete': cmd_settings_delete,
        'settings-compare': cmd_settings_compare,
        'settings-export': cmd_settings_export,
        'settings-import': cmd_settings_import,
        'settings-validate': cmd_settings_validate,
        'settings-templates': cmd_settings_templates
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
