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
    cmd_repo_create_queue,
    cmd_repo_create_test_images,
    cmd_repo_gpu_configure,
    cmd_repo_gpu_status,
    cmd_repo_init,
    cmd_repo_list,
    cmd_repo_list_queues,
    cmd_repo_people,
    cmd_repo_queue_stats,
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
        '--person',
        required=True,
        help='Person name (mandatory)'
    )
    parser_add.add_argument(
        '--name',
        help='Optional descriptive name for this face (e.g., "frontal", "profile")'
    )
    parser_add.add_argument(
        '--tags',
        help='Comma-separated tags'
    )
    parser_add.add_argument(
        '--preview',
        action='store_true',
        help='Generate preview before adding to repository'
    )

    # repo-list
    parser_list = subparsers.add_parser(
        'list',
        help='List faces in repository'
    )
    parser_list.add_argument(
        '--person',
        help='Filter by person name'
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
    parser_stats.add_argument(
        '--person',
        help='Show statistics for specific person'
    )

    # repo-people
    parser_people = subparsers.add_parser(
        'people',
        help='List all people in repository'
    )

    # gpu-status
    parser_gpu_status = subparsers.add_parser(
        'gpu-status',
        help='Show GPU status and configuration'
    )

    # gpu-configure
    parser_gpu_config = subparsers.add_parser(
        'gpu-configure',
        help='Configure GPU settings'
    )
    parser_gpu_config.add_argument(
        '--enable',
        action='store_true',
        help='Enable GPU acceleration'
    )
    parser_gpu_config.add_argument(
        '--disable',
        action='store_true',
        help='Disable GPU acceleration'
    )
    parser_gpu_config.add_argument(
        '--device-ids',
        help='Comma-separated device IDs to use (e.g., "0,1")'
    )
    parser_gpu_config.add_argument(
        '--memory-limit',
        type=int,
        help='GPU memory limit in MB'
    )

    # create-test-images
    parser_create_test = subparsers.add_parser(
        'create-test-images',
        help='Create test images from source directory'
    )
    parser_create_test.add_argument(
        '--source-dir',
        required=True,
        help='Directory containing reference images'
    )
    parser_create_test.add_argument(
        '--output-dir',
        help='Output directory for test images (default: repository test_images/)'
    )

    # create-queue
    parser_create_queue = subparsers.add_parser(
        'create-queue',
        help='Create processing queue with FaceFusion destination selection'
    )
    parser_create_queue.add_argument(
        '--person',
        required=True,
        help='Person name'
    )
    parser_create_queue.add_argument(
        '--face-id',
        required=True,
        help='Source face ID'
    )
    parser_create_queue.add_argument(
        '--destination',
        required=True,
        help='Destination media path (video or image)'
    )
    parser_create_queue.add_argument(
        '--face-selector',
        default='reference',
        choices=['reference', 'one', 'many', 'best-quality', 'all'],
        help='FaceFusion face selector mode (default: reference)'
    )
    parser_create_queue.add_argument(
        '--face-index',
        type=int,
        help='Face index for "one" selector mode'
    )
    parser_create_queue.add_argument(
        '--reference-face-distance',
        type=float,
        default=0.6,
        help='Reference face distance threshold (default: 0.6)'
    )
    parser_create_queue.add_argument(
        '--settings',
        help='Processing settings profile name'
    )

    # list-queues
    parser_list_queues = subparsers.add_parser(
        'list-queues',
        help='List processing queues'
    )
    parser_list_queues.add_argument(
        '--status',
        choices=['pending', 'processing', 'completed', 'failed'],
        help='Filter by status'
    )

    # queue-stats
    parser_queue_stats = subparsers.add_parser(
        'queue-stats',
        help='Show queue statistics'
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
        'people': cmd_repo_people,
        'gpu-status': cmd_repo_gpu_status,
        'gpu-configure': cmd_repo_gpu_configure,
        'create-test-images': cmd_repo_create_test_images,
        'create-queue': cmd_repo_create_queue,
        'list-queues': cmd_repo_list_queues,
        'queue-stats': cmd_repo_queue_stats
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
