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
    cmd_repo_init,
    cmd_repo_list,
    cmd_repo_remove,
    cmd_repo_show,
    cmd_repo_stats,
    cmd_analyze_destination,
    cmd_show_queues,
    cmd_export_queue,
    cmd_clear_queues,
    cmd_queue_stats,
    cmd_batch_run,
    cmd_batch_status
)


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

    # analyze-destination
    parser_analyze = subparsers.add_parser(
        'analyze-destination',
        help='Analyze destination media and create processing queues'
    )
    parser_analyze.add_argument(
        '--source',
        required=True,
        help='Path to destination image or video'
    )
    parser_analyze.add_argument(
        '--frame-sample-rate',
        type=int,
        default=1,
        help='For videos, process every Nth frame (default: 1)'
    )
    parser_analyze.add_argument(
        '--min-confidence',
        type=float,
        default=0.5,
        help='Minimum match confidence (0.0-1.0, default: 0.5)'
    )
    parser_analyze.add_argument(
        '--no-queues',
        action='store_true',
        help='Do not create processing queues (analysis only)'
    )

    # show-queues
    parser_show_queues = subparsers.add_parser(
        'show-queues',
        help='Display current processing queues'
    )

    # export-queue
    parser_export = subparsers.add_parser(
        'export-queue',
        help='Export specific queue to JSON file'
    )
    parser_export.add_argument(
        '--face-id',
        required=True,
        help='Source face ID of queue to export'
    )
    parser_export.add_argument(
        '--output',
        required=True,
        help='Output JSON file path'
    )

    # clear-queues
    parser_clear = subparsers.add_parser(
        'clear-queues',
        help='Clear all or specific processing queues'
    )
    parser_clear.add_argument(
        '--face-id',
        help='Source face ID to clear (if not specified, clears all)'
    )

    # queue-stats
    parser_queue_stats = subparsers.add_parser(
        'queue-stats',
        help='Show detailed queue statistics'
    )

    # batch-run
    parser_batch_run = subparsers.add_parser(
        'batch-run',
        help='Execute batch face swap processing'
    )
    parser_batch_run.add_argument(
        '--output',
        required=True,
        help='Output directory for processed files'
    )
    parser_batch_run.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview operations without executing'
    )

    # batch-status
    parser_batch_status = subparsers.add_parser(
        'batch-status',
        help='Show batch processing status'
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
        'analyze-destination': cmd_analyze_destination,
        'show-queues': cmd_show_queues,
        'export-queue': cmd_export_queue,
        'clear-queues': cmd_clear_queues,
        'queue-stats': cmd_queue_stats,
        'batch-run': cmd_batch_run,
        'batch-status': cmd_batch_status
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
