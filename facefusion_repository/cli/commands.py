"""
CLI commands for FaceFusion Repository System.
"""

import argparse

from facefusion_repository.repository.compatibility_matrix import CompatibilityMatrix
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.destination.analyzer import DestinationAnalyzer
from facefusion_repository.destination.queue_manager import QueueManager


# Constants
# NOTE: This estimate is based on average GPU processing time for face swapping.
# Actual time varies based on hardware (CPU vs GPU), image resolution,
# and face detection complexity. This value may need adjustment based on
# system capabilities and can be made configurable in future versions.
ESTIMATED_SECONDS_PER_FACE_SWAP = 0.5  # Average time estimate for processing a single face swap


def register_repository_commands(subparsers: argparse._SubParsersAction) -> None:
    """
    Register repository commands with the argument parser.

    Args:
        subparsers: Subparser object from argparse
    """
    # repo-init command
    parser_init = subparsers.add_parser(
        'repo-init',
        help='Initialize face repository'
    )
    parser_init.set_defaults(func=cmd_repo_init)

    # repo-add-face command
    parser_add = subparsers.add_parser(
        'repo-add-face',
        help='Add face to repository'
    )
    parser_add.add_argument(
        '--source',
        required=True,
        help='Path to face image'
    )
    parser_add.add_argument(
        '--character',
        '--character-name',
        dest='character_name',
        required=True,
        help='Character/person name (primary identifier)'
    )
    parser_add.add_argument(
        '--face-name',
        help='Optional specific name for this face variant (e.g., "frontal", "profile_left")'
    )
    parser_add.add_argument(
        '--name',
        help='[DEPRECATED] Use --character instead. For backward compatibility only.'
    )
    parser_add.add_argument(
        '--tags',
        help='Comma-separated tags'
    )
    parser_add.add_argument(
        '--yaw',
        type=float,
        help='Manual yaw angle (horizontal rotation, -180 to 180)'
    )
    parser_add.add_argument(
        '--pitch',
        type=float,
        help='Manual pitch angle (vertical tilt, -90 to 90)'
    )
    parser_add.add_argument(
        '--roll',
        type=float,
        help='Manual roll angle (head tilt, -180 to 180)'
    )
    parser_add.set_defaults(func=cmd_repo_add_face)

    # repo-list command
    parser_list = subparsers.add_parser(
        'repo-list',
        help='List faces in repository'
    )
    parser_list.add_argument(
        '--character',
        '--character-name',
        dest='character_name',
        help='Filter by character/person name'
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
    parser_list.set_defaults(func=cmd_repo_list)

    # repo-show command
    parser_show = subparsers.add_parser(
        'repo-show',
        help='Show face details'
    )
    parser_show.add_argument(
        '--face-id',
        required=True,
        help='Face ID to show'
    )
    parser_show.set_defaults(func=cmd_repo_show)

    # repo-remove command
    parser_remove = subparsers.add_parser(
        'repo-remove',
        help='Remove face from repository'
    )
    parser_remove.add_argument(
        '--face-id',
        required=True,
        help='Face ID to remove'
    )
    parser_remove.set_defaults(func=cmd_repo_remove)

    # repo-stats command
    parser_stats = subparsers.add_parser(
        'repo-stats',
        help='Show repository statistics'
    )
    parser_stats.set_defaults(func=cmd_repo_stats)

    # analyze-destination command
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
    parser_analyze.set_defaults(func=cmd_analyze_destination)

    # show-queues command
    parser_show_queues = subparsers.add_parser(
        'show-queues',
        help='Display current processing queues'
    )
    parser_show_queues.set_defaults(func=cmd_show_queues)

    # export-queue command
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
    parser_export.set_defaults(func=cmd_export_queue)

    # clear-queues command
    parser_clear = subparsers.add_parser(
        'clear-queues',
        help='Clear all or specific processing queues'
    )
    parser_clear.add_argument(
        '--face-id',
        help='Source face ID to clear (if not specified, clears all)'
    )
    parser_clear.set_defaults(func=cmd_clear_queues)

    # queue-stats command
    parser_queue_stats = subparsers.add_parser(
        'queue-stats',
        help='Show detailed queue statistics'
    )
    parser_queue_stats.set_defaults(func=cmd_queue_stats)


def cmd_repo_init(args: argparse.Namespace) -> int:
    """
    Initialize repository command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    print('Initializing FaceFusion Repository...')

    repo = RepositoryManager()

    if repo.initialize_repository():
        print('✓ Repository initialized successfully at {}'.format(repo.repository_path))
        return 0
    else:
        print('✗ Failed to initialize repository')
        return 1


def cmd_repo_add_face(args: argparse.Namespace) -> int:
    """
    Add face to repository command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    print(f'Adding face from: {args.source}')

    # Parse tags if provided
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]

    repo = RepositoryManager()
    face_id = repo.add_face(
        image_path=args.source,
        name=args.name,
        tags=tags
    )

    if face_id:
        print('✓ Face added successfully!')
        print('  ID: {}'.format(face_id))
        if args.name:
            print('  Name: {}'.format(args.name))
        if tags:
            print('  Tags: {}'.format(', '.join(tags)))

        # Show face details
        face = repo.get_face(face_id)
        if face:
            print('  Orientation: {}°'.format(face.orientation_angle))
            print('  Quality: {:.2f}'.format(face.quality_metrics.overall_quality))
            print('  Resolution: {}x{}'.format(face.quality_metrics.resolution[0], face.quality_metrics.resolution[1]))
        return 0
    else:
        print('✗ Failed to add face (see error messages above)')
        return 1


def cmd_repo_list(args: argparse.Namespace) -> int:
    """
    List faces in repository command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    # Parse tags if provided
    filter_tags = None
    if args.tags:
        filter_tags = [tag.strip() for tag in args.tags.split(',')]

    repo = RepositoryManager()
    faces = repo.list_faces(
        filter_by_orientation=args.orientation,
        filter_by_tags=filter_tags
    )

    if not faces:
        print('No faces found in repository.')
        if args.orientation or filter_tags:
            print('Try removing filters to see all faces.')
        return 0

    print('Found {} face(s):'.format(len(faces)))
    print()

    for face in faces:
        print('ID: {}'.format(face.id))
        print('  Name: {}'.format(face.metadata.name or 'Unnamed'))
        print('  Orientation: {}°'.format(face.orientation_angle))
        print('  Quality: {:.2f}'.format(face.quality_metrics.overall_quality))
        print('  Resolution: {}x{}'.format(face.quality_metrics.resolution[0], face.quality_metrics.resolution[1]))
        if face.metadata.tags:
            print('  Tags: {}'.format(', '.join(face.metadata.tags)))
        print('  Added: {}'.format(face.metadata.added_date))
        print()

    return 0


def cmd_repo_show(args: argparse.Namespace) -> int:
    """
    Show face details command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    repo = RepositoryManager()
    face = repo.get_face(args.face_id)

    if not face:
        print('✗ Face not found: {}'.format(args.face_id))
        return 1

    print('Face Details: {}'.format(args.face_id))
    print('=' * 60)
    print()
    print('Name: {}'.format(face.metadata.name or 'Unnamed'))
    print('File: {}'.format(face.file_path))
    print('Orientation: {}°'.format(face.orientation_angle))
    print()
    print('Quality Metrics:')
    print('  Resolution: {}x{}'.format(face.quality_metrics.resolution[0], face.quality_metrics.resolution[1]))
    print('  Sharpness: {:.3f}'.format(face.quality_metrics.sharpness))
    print('  Brightness: {:.3f}'.format(face.quality_metrics.brightness))
    print('  Contrast: {:.3f}'.format(face.quality_metrics.contrast))
    print('  Detector Score: {:.3f}'.format(face.quality_metrics.detector_score))
    print('  Overall Quality: {:.3f}'.format(face.quality_metrics.overall_quality))
    print()
    if face.metadata.tags:
        print('Tags: {}'.format(', '.join(face.metadata.tags)))
    print('Added: {}'.format(face.metadata.added_date))

    return 0


def cmd_repo_remove(args: argparse.Namespace) -> int:
    """
    Remove face from repository command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    print(f'Removing face: {args.face_id}')

    repo = RepositoryManager()

    if repo.remove_face(args.face_id):
        print('✓ Face removed successfully')
        return 0
    else:
        print('✗ Failed to remove face')
        return 1


def cmd_repo_stats(args: argparse.Namespace) -> int:
    """
    Show repository statistics command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    repo = RepositoryManager()
    matrix = CompatibilityMatrix(repo)

    # Show compatibility matrix visualization
    print(matrix.visualize_matrix())
    print()

    # Show coverage report
    coverage = matrix.get_coverage_report()

    print('Coverage Report:')
    print('-' * 60)
    print(f'Total Standard Orientations: {coverage.total_orientations}')
    print(f'Covered Orientations: {len(coverage.covered_orientations)}')
    print(f'Coverage: {coverage.coverage_percentage:.1f}%')

    if coverage.missing_orientations:
        print(f'\nMissing Orientations: {", ".join(str(a) + "°" for a in coverage.missing_orientations)}')
        print('\nRecommendation: Add faces at missing orientations for complete coverage.')

    return 0


def cmd_analyze_destination(args: argparse.Namespace) -> int:
    """
    Analyze destination media command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    print(f'Analyzing destination media: {args.source}')
    print()

    # Initialize analyzer
    analyzer = DestinationAnalyzer()

    # Progress callback for videos
    def progress_callback(current: int, total: int, message: str) -> None:
        if current % 30 == 0 or current == total - 1:  # Update every 30 frames
            percent = (current / total * 100) if total > 0 else 0
            print(f'  {message} ({percent:.1f}%)')

    try:
        # Analyze media
        result = analyzer.analyze_media(
            media_path=args.source,
            frame_sample_rate=args.frame_sample_rate,
            min_confidence=args.min_confidence,
            create_queues=not args.no_queues,
            progress_callback=progress_callback
        )

        if not result:
            print('✗ Failed to analyze media (unsupported format or error)')
            return 1

        # Display results
        print()
        print('Analysis Complete!')
        print('=' * 60)
        print(f'Source File: {result.source_file}')
        print(f'Total Faces Detected: {result.total_faces_detected}')
        print(f'Total Faces Matched: {result.total_faces_matched}')

        if result.total_faces_detected > 0:
            match_rate = result.total_faces_matched / result.total_faces_detected * 100
            print(f'Match Rate: {match_rate:.1f}%')

        print(f'Processing Time: {result.processing_time:.2f}s')
        print()

        # Show match summary
        summary = result.get_summary()
        if summary['matches_by_face']:
            print('Matches by Repository Face:')
            for face_id, count in summary['matches_by_face'].items():
                # Get face name
                repo = RepositoryManager()
                face = repo.get_face(face_id)
                name = face.metadata.name if face and face.metadata.name else 'Unnamed'
                print(f'  {face_id} ({name}): {count} matches')
            print()

        if not args.no_queues and result.total_faces_matched > 0:
            print('✓ Processing queues created successfully')
            print('  Use "show-queues" to view queues')

        return 0

    except Exception as e:
        print(f'✗ Error analyzing destination: {e}')
        import traceback
        traceback.print_exc()
        return 1


def cmd_show_queues(args: argparse.Namespace) -> int:
    """
    Show processing queues command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    queue_manager = QueueManager()
    queues = queue_manager.list_queues()

    if not queues:
        print('No processing queues found.')
        print('Use "analyze-destination" to create queues.')
        return 0

    print('Processing Queues:')
    print('=' * 60)
    print()

    repo = RepositoryManager()

    for queue in queues:
        face = repo.get_face(queue.source_face_id)
        face_name = face.metadata.name if face and face.metadata.name else 'Unnamed'

        print(f'Queue: {queue.source_face_id}')
        print(f'  Name: {face_name}')
        print(f'  Matches: {queue.get_size()}')
        print(f'  Average Confidence: {queue.get_average_confidence():.2f}')
        print(f'  Created: {queue.created_date}')
        print()

    # Show statistics
    stats = queue_manager.get_statistics()
    print('Summary:')
    print('-' * 60)
    print(f'Total Queues: {stats.total_queues}')
    print(f'Total Faces: {stats.total_faces}')

    return 0


def cmd_export_queue(args: argparse.Namespace) -> int:
    """
    Export queue command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    queue_manager = QueueManager()

    if queue_manager.export_queue(args.face_id, args.output):
        print(f'✓ Queue exported successfully to: {args.output}')
        return 0
    else:
        print(f'✗ Failed to export queue (queue not found or error)')
        return 1


def cmd_clear_queues(args: argparse.Namespace) -> int:
    """
    Clear queues command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    queue_manager = QueueManager()

    if args.face_id:
        # Clear specific queue
        if queue_manager.clear_queue(args.face_id):
            print(f'✓ Queue cleared: {args.face_id}')
            return 0
        else:
            print(f'✗ Failed to clear queue (not found or error)')
            return 1
    else:
        # Clear all queues
        if queue_manager.clear_all_queues():
            print('✓ All queues cleared')
            return 0
        else:
            print('✗ Failed to clear queues')
            return 1


def cmd_queue_stats(args: argparse.Namespace) -> int:
    """
    Show queue statistics command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    queue_manager = QueueManager()
    stats = queue_manager.get_statistics()

    if stats.total_queues == 0:
        print('No processing queues found.')
        return 0

    print('Queue Statistics:')
    print('=' * 60)
    print()
    print(f'Total Queues: {stats.total_queues}')
    print(f'Total Faces: {stats.total_faces}')
    print()

    if stats.faces_per_queue:
        print('Faces per Queue:')
        repo = RepositoryManager()

        # Sort by face count descending
        sorted_queues = sorted(
            stats.faces_per_queue.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for face_id, count in sorted_queues:
            face = repo.get_face(face_id)
            name = face.metadata.name if face and face.metadata.name else 'Unnamed'
            print(f'  {face_id} ({name}): {count} faces')

    return 0


def cmd_batch_run(args: argparse.Namespace) -> int:
    """
    Execute batch processing command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    from facefusion_repository.batch.executor import BatchExecutor

    print('Initializing batch executor...')
    print()

    # Initialize components
    repo_manager = RepositoryManager()
    queue_manager = QueueManager()
    executor = BatchExecutor(queue_manager, repo_manager)
    
    # Check dry_run flag
    dry_run_mode = getattr(args, 'dry_run', False)

    # Progress callback
    def progress_callback(current: int, total: int) -> None:
        percent = (current / total) * 100 if total > 0 else 0
        if current % 10 == 0 or current == total:
            print(f'Progress: {current}/{total} ({percent:.1f}%)')

    try:
        # Execute batch processing
        result = executor.execute_all_queues(
            output_path=args.output,
            progress_callback=progress_callback,
            dry_run=dry_run_mode
        )

        if dry_run_mode:
            return 0

        # Display results
        print()
        print('=' * 60)
        print('Batch Execution Complete!')
        print('=' * 60)
        print()
        print(f'Total queues processed: {result.total_queues}')
        print(f'Successful: {result.successful}')
        print(f'Failed: {result.failed}')
        print(f'Total faces processed: {result.total_faces_processed}')
        print(f'Total time: {result.total_time:.2f}s')
        print()

        # Show per-queue results
        if result.queue_results:
            print('Per-Queue Results:')
            print('-' * 60)
            for qr in result.queue_results:
                status = '✓' if qr.success else '✗'
                print(f'{status} Queue: {qr.queue_id}')
                if qr.success:
                    print(f'  Faces processed: {qr.faces_processed}')
                    print(f'  Time: {qr.processing_time:.2f}s')
                    if qr.output_file:
                        print(f'  Output: {qr.output_file}')
                else:
                    print(f'  Error: {qr.error}')
                print()

        return 0 if result.failed == 0 else 1

    except Exception as e:
        print(f'Error during batch execution: {e}')
        import traceback
        traceback.print_exc()
        return 1


def cmd_batch_status(args: argparse.Namespace) -> int:
    """
    Show batch processing status command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    # Get queue statistics
    queue_manager = QueueManager()
    stats = queue_manager.get_statistics()

    if stats.total_queues == 0:
        print('No processing queues available.')
        print('Use "analyze-destination" command to create queues.')
        return 0

    print('Batch Processing Status:')
    print('=' * 60)
    print()
    print(f'Total Queues Ready: {stats.total_queues}')
    print(f'Total Faces to Process: {stats.total_faces}')
    print()

    # Estimate processing time
    estimated_time = stats.total_faces * ESTIMATED_SECONDS_PER_FACE_SWAP
    hours = int(estimated_time / 3600)
    minutes = int((estimated_time % 3600) / 60)
    seconds = int(estimated_time % 60)

    print(f'Estimated Processing Time: ', end='')
    if hours > 0:
        print(f'{hours}h {minutes}m {seconds}s')
    elif minutes > 0:
        print(f'{minutes}m {seconds}s')
    else:
        print(f'{seconds}s')

    print()
    print('Run "batch-run --output <directory>" to start processing.')

    return 0
