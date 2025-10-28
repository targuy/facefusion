#!/usr/bin/env python3
"""
Standalone CLI for FaceFusion Repository System.

This provides a simple command-line interface to test and use the repository
system independently.
"""

import argparse
import sys

from facefusion_repository.cli.commands import (
    cmd_presets_apply,
    cmd_presets_copy,
    cmd_presets_create,
    cmd_presets_delete,
    cmd_presets_export,
    cmd_presets_import,
    cmd_presets_list,
    cmd_presets_show,
    cmd_presets_update,
    cmd_presets_validate,
    cmd_repo_add_face,
    cmd_repo_init,
    cmd_repo_list,
    cmd_repo_remove,
    cmd_repo_show,
    cmd_repo_stats,
    cmd_settings_create,
    cmd_settings_delete,
    cmd_settings_export,
    cmd_settings_import,
    cmd_settings_list,
    cmd_settings_show
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

    # Repository commands
    # repo-init
    subparsers.add_parser(
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
    subparsers.add_parser(
        'stats',
        help='Show repository statistics'
    )

    # Settings commands
    # settings-create
    parser_settings_create = subparsers.add_parser(
        'settings-create',
        help='Create settings profile'
    )
    parser_settings_create.add_argument('--name', required=True, help='Profile name')
    parser_settings_create.add_argument('--file', help='JSON file with settings')
    parser_settings_create.add_argument('--template', help='Use template')
    parser_settings_create.add_argument('--description', help='Description')

    # settings-list
    subparsers.add_parser(
        'settings-list',
        help='List settings profiles'
    )

    # settings-show
    parser_settings_show = subparsers.add_parser(
        'settings-show',
        help='Show settings profile'
    )
    parser_settings_show.add_argument('--name', required=True, help='Profile name')

    # settings-delete
    parser_settings_delete = subparsers.add_parser(
        'settings-delete',
        help='Delete settings profile'
    )
    parser_settings_delete.add_argument('--name', required=True, help='Profile name')

    # settings-export
    parser_settings_export = subparsers.add_parser(
        'settings-export',
        help='Export settings profile'
    )
    parser_settings_export.add_argument('--name', required=True, help='Profile name')
    parser_settings_export.add_argument('--output', required=True, help='Output file')

    # settings-import
    parser_settings_import = subparsers.add_parser(
        'settings-import',
        help='Import settings profile'
    )
    parser_settings_import.add_argument('--file', required=True, help='Input file')
    parser_settings_import.add_argument('--name', help='New profile name')

    # Presets commands
    # presets-create
    parser_presets_create = subparsers.add_parser(
        'presets-create',
        help='Create new preset'
    )
    parser_presets_create.add_argument('--name', required=True, help='Preset name')
    parser_presets_create.add_argument('--face-id', required=True, help='Face ID')
    parser_presets_create.add_argument('--settings', required=True, help='Settings profile')
    parser_presets_create.add_argument('--description', help='Description')
    parser_presets_create.add_argument('--tags', help='Comma-separated tags')

    # presets-list
    parser_presets_list = subparsers.add_parser(
        'presets-list',
        help='List all presets'
    )
    parser_presets_list.add_argument('--face-id', help='Filter by face ID')
    parser_presets_list.add_argument('--settings', help='Filter by settings profile')

    # presets-show
    parser_presets_show = subparsers.add_parser(
        'presets-show',
        help='Show preset details'
    )
    parser_presets_show.add_argument('--name', required=True, help='Preset name')

    # presets-update
    parser_presets_update = subparsers.add_parser(
        'presets-update',
        help='Update preset'
    )
    parser_presets_update.add_argument('--name', required=True, help='Preset name')
    parser_presets_update.add_argument('--face-id', help='New face ID')
    parser_presets_update.add_argument('--settings', help='New settings profile')
    parser_presets_update.add_argument('--description', help='New description')

    # presets-delete
    parser_presets_delete = subparsers.add_parser(
        'presets-delete',
        help='Delete preset'
    )
    parser_presets_delete.add_argument('--name', required=True, help='Preset name')

    # presets-validate
    parser_presets_validate = subparsers.add_parser(
        'presets-validate',
        help='Validate preset'
    )
    parser_presets_validate.add_argument('--name', required=True, help='Preset name')

    # presets-copy
    parser_presets_copy = subparsers.add_parser(
        'presets-copy',
        help='Copy preset'
    )
    parser_presets_copy.add_argument('--source', required=True, help='Source preset')
    parser_presets_copy.add_argument('--name', required=True, help='New preset name')
    parser_presets_copy.add_argument('--face-id', help='Override face ID')
    parser_presets_copy.add_argument('--settings', help='Override settings profile')

    # presets-export
    parser_presets_export = subparsers.add_parser(
        'presets-export',
        help='Export preset'
    )
    parser_presets_export.add_argument('--name', required=True, help='Preset name')
    parser_presets_export.add_argument('--output', required=True, help='Output file')

    # presets-import
    parser_presets_import = subparsers.add_parser(
        'presets-import',
        help='Import preset'
    )
    parser_presets_import.add_argument('--file', required=True, help='Input file')
    parser_presets_import.add_argument('--name', help='New preset name')

    # presets-apply
    parser_presets_apply = subparsers.add_parser(
        'presets-apply',
        help='Show preset configuration'
    )
    parser_presets_apply.add_argument('--name', required=True, help='Preset name')

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
        'settings-delete': cmd_settings_delete,
        'settings-export': cmd_settings_export,
        'settings-import': cmd_settings_import,
        'presets-create': cmd_presets_create,
        'presets-list': cmd_presets_list,
        'presets-show': cmd_presets_show,
        'presets-update': cmd_presets_update,
        'presets-delete': cmd_presets_delete,
        'presets-validate': cmd_presets_validate,
        'presets-copy': cmd_presets_copy,
        'presets-export': cmd_presets_export,
        'presets-import': cmd_presets_import,
        'presets-apply': cmd_presets_apply
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
