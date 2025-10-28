"""
CLI commands for FaceFusion Repository System.
"""

import argparse

from facefusion_repository.repository.compatibility_matrix import CompatibilityMatrix
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.gpu.manager import GPUManager
from facefusion_repository.preview.test_image_manager import TestImageManager
from facefusion_repository.preview.preview_generator import PreviewGenerator
from facefusion_repository.queue.manager import QueueManager


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
    parser_add.set_defaults(func=cmd_repo_add_face)

    # repo-list command
    parser_list = subparsers.add_parser(
        'repo-list',
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
    parser_stats.add_argument(
        '--person',
        help='Show statistics for specific person'
    )
    parser_stats.set_defaults(func=cmd_repo_stats)

    # repo-people command
    parser_people = subparsers.add_parser(
        'repo-people',
        help='List all people in repository'
    )
    parser_people.set_defaults(func=cmd_repo_people)

    # repo-gpu-status command
    parser_gpu_status = subparsers.add_parser(
        'repo-gpu-status',
        help='Show GPU status and configuration'
    )
    parser_gpu_status.set_defaults(func=cmd_repo_gpu_status)

    # repo-gpu-configure command
    parser_gpu_config = subparsers.add_parser(
        'repo-gpu-configure',
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
    parser_gpu_config.set_defaults(func=cmd_repo_gpu_configure)

    # repo-create-test-images command
    parser_create_test = subparsers.add_parser(
        'repo-create-test-images',
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
    parser_create_test.set_defaults(func=cmd_repo_create_test_images)

    # repo-create-queue command
    parser_create_queue = subparsers.add_parser(
        'repo-create-queue',
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
    parser_create_queue.set_defaults(func=cmd_repo_create_queue)

    # repo-list-queues command
    parser_list_queues = subparsers.add_parser(
        'repo-list-queues',
        help='List processing queues'
    )
    parser_list_queues.add_argument(
        '--status',
        choices=['pending', 'processing', 'completed', 'failed'],
        help='Filter by status'
    )
    parser_list_queues.set_defaults(func=cmd_repo_list_queues)

    # repo-queue-stats command
    parser_queue_stats = subparsers.add_parser(
        'repo-queue-stats',
        help='Show queue statistics'
    )
    parser_queue_stats.set_defaults(func=cmd_repo_queue_stats)


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
    print(f'Adding face for {args.person} from: {args.source}')

    # Generate preview if requested
    if args.preview:
        print('\nGenerating preview...')
        preview_gen = PreviewGenerator()
        result = preview_gen.generate_preview(args.source)
        
        if result.success:
            print('✓ Preview generated successfully')
            print(f'  Preview path: {result.preview_path}')
            print(f'  Quality score: {result.quality_score:.2f}')
            if result.orientation_match:
                print(f'  Orientation match: {result.orientation_match}')
            
            if result.warnings:
                print('  Warnings:')
                for warning in result.warnings:
                    print(f'    - {warning}')
            
            # Ask for confirmation
            response = input('\nProceed with adding face to repository? (y/n): ')
            if response.lower() != 'y':
                print('Cancelled.')
                return 0
        else:
            print('✗ Preview generation failed')
            for warning in result.warnings:
                print(f'  - {warning}')
            print('Continuing without preview...')

    # Parse tags if provided
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]

    repo = RepositoryManager()
    face_id = repo.add_face(
        image_path=args.source,
        person=args.person,
        name=args.name,
        tags=tags
    )

    if face_id:
        print('✓ Face added successfully!')
        print('  ID: {}'.format(face_id))
        print('  Person: {}'.format(args.person))
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
        filter_by_person=args.person,
        filter_by_orientation=args.orientation,
        filter_by_tags=filter_tags
    )

    if not faces:
        print('No faces found in repository.')
        if args.person or args.orientation or filter_tags:
            print('Try removing filters to see all faces.')
        return 0

    print('Found {} face(s):'.format(len(faces)))
    print()

    for face in faces:
        print('ID: {}'.format(face.id))
        print('  Person: {}'.format(face.metadata.person))
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
    print('Person: {}'.format(face.metadata.person))
    print('Name: {}'.format(face.metadata.name or 'Unnamed'))
    print('File: {}'.format(face.file_path))
    print('Orientation: {}°'.format(face.orientation_angle))
    print()
    
    # Display 3D pose if available
    if face.pitch is not None or face.yaw is not None or face.tilt is not None:
        print('3D Pose:')
        if face.pitch is not None:
            print('  Pitch (up/down): {:.1f}°'.format(face.pitch))
        if face.yaw is not None:
            print('  Yaw (left/right): {:.1f}°'.format(face.yaw))
        if face.tilt is not None:
            print('  Tilt (rotation): {:.1f}°'.format(face.tilt))
        print()
    
    # Display occlusion info if available
    if face.occlusion_score is not None:
        print('Occlusion:')
        print('  Score: {:.2f}'.format(face.occlusion_score))
        if face.occlusion_score == 0:
            print('  Status: No occlusion detected')
        elif face.occlusion_score < 0.3:
            print('  Status: Minor occlusion')
        elif face.occlusion_score < 0.6:
            print('  Status: Moderate occlusion')
        else:
            print('  Status: Severe occlusion')
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
    
    # If person is specified, show person-specific stats
    if hasattr(args, 'person') and args.person:
        stats = repo.get_person_statistics(args.person)
        if not stats:
            print(f'No faces found for person: {args.person}')
            return 1
        
        print(f'Statistics for {args.person}:')
        print('-' * 60)
        print(f'Total Faces: {stats.total_faces}')
        print(f'Average Quality: {stats.average_quality:.2f}')
        print(f'Total Size: {stats.total_size_mb:.2f} MB')
        print()
        print('Faces by Orientation:')
        for angle in sorted(stats.faces_by_orientation.keys()):
            count = stats.faces_by_orientation[angle]
            print(f'  {angle}°: {count} face(s)')
        
        return 0
    
    # Show overall repository stats
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
    
    # Show people count
    people = repo.list_people()
    print(f'\nTotal People: {len(people)}')
    if people:
        print('People in repository:')
        for person in people:
            person_faces = repo.list_faces(filter_by_person=person)
            print(f'  - {person}: {len(person_faces)} face(s)')

    return 0


def cmd_repo_people(args: argparse.Namespace) -> int:
    """
    List all people in repository command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    repo = RepositoryManager()
    people = repo.list_people()

    if not people:
        print('No people found in repository.')
        return 0

    print('People in repository:')
    print('-' * 60)
    
    for person in people:
        faces = repo.list_faces(filter_by_person=person)
        stats = repo.get_person_statistics(person)
        
        print(f'\n{person}:')
        print(f'  Total Faces: {len(faces)}')
        if stats:
            print(f'  Average Quality: {stats.average_quality:.2f}')
            print(f'  Orientations: {", ".join(str(a) + "°" for a in sorted(stats.faces_by_orientation.keys()))}')

    return 0


def cmd_repo_gpu_status(args: argparse.Namespace) -> int:
    """
    Show GPU status and configuration command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    gpu_manager = GPUManager()
    gpu_manager.print_status()
    return 0


def cmd_repo_gpu_configure(args: argparse.Namespace) -> int:
    """
    Configure GPU settings command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    gpu_manager = GPUManager()
    
    # Check for conflicting options
    if args.enable and args.disable:
        print('Error: Cannot enable and disable GPU at the same time')
        return 1
    
    # Enable GPU
    if args.enable:
        device_ids = None
        if args.device_ids:
            try:
                device_ids = [int(x.strip()) for x in args.device_ids.split(',')]
            except ValueError:
                print('Error: Invalid device IDs format. Use comma-separated integers.')
                return 1
        
        if gpu_manager.enable_gpu(device_ids):
            print('✓ GPU acceleration enabled')
        else:
            print('✗ Failed to enable GPU acceleration')
            return 1
    
    # Disable GPU
    if args.disable:
        if gpu_manager.disable_gpu():
            print('✓ GPU acceleration disabled (CPU only)')
        else:
            print('✗ Failed to disable GPU acceleration')
            return 1
    
    # Set memory limit
    if args.memory_limit:
        if gpu_manager.set_memory_limit(args.memory_limit):
            print(f'✓ GPU memory limit set to {args.memory_limit} MB')
        else:
            print('✗ Failed to set GPU memory limit')
            return 1
    
    # Show current status
    print()
    gpu_manager.print_status()
    
    return 0


def cmd_repo_create_test_images(args: argparse.Namespace) -> int:
    """
    Create test images from source directory command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    print(f'Creating test images from: {args.source_dir}')
    
    test_manager = TestImageManager()
    
    count = test_manager.create_test_images_from_directory(
        source_dir=args.source_dir,
        output_dir=args.output_dir
    )
    
    if count > 0:
        print(f'\n✓ Successfully created {count} test images')
        
        # Show coverage
        coverage = test_manager.get_coverage()
        print(f'\nCoverage: {coverage["coverage_percentage"]:.1f}%')
        print(f'Covered orientations: {", ".join(str(a) + "°" for a in coverage["covered_angles"])}')
        
        if coverage['missing_angles']:
            print(f'Missing orientations: {", ".join(str(a) + "°" for a in coverage["missing_angles"])}')
        
        return 0
    else:
        print('✗ No test images were created')
        return 1


def cmd_repo_create_queue(args: argparse.Namespace) -> int:
    """
    Create processing queue command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    print(f'Creating queue for {args.person}...')
    
    # Verify face exists
    repo = RepositoryManager()
    face = repo.get_face(args.face_id)
    
    if not face:
        print(f'✗ Face not found: {args.face_id}')
        return 1
    
    if face.metadata.person != args.person:
        print(f'✗ Face {args.face_id} does not belong to person {args.person}')
        return 1
    
    # Create queue
    queue_manager = QueueManager()
    
    try:
        queue_id = queue_manager.create_queue(
            person=args.person,
            face_id=args.face_id,
            destination_media=args.destination,
            face_selector_mode=args.face_selector,
            face_index=args.face_index,
            reference_face_distance=args.reference_face_distance,
            processing_settings=args.settings
        )
        
        print('✓ Queue created successfully')
        print(f'  Queue ID: {queue_id}')
        print(f'  Person: {args.person}')
        print(f'  Face ID: {args.face_id}')
        print(f'  Destination: {args.destination}')
        print(f'  Face Selector Mode: {args.face_selector}')
        
        if args.face_index is not None:
            print(f'  Face Index: {args.face_index}')
        
        print(f'  Reference Face Distance: {args.reference_face_distance}')
        
        if args.settings:
            print(f'  Settings Profile: {args.settings}')
        
        return 0
        
    except Exception as e:
        print(f'✗ Failed to create queue: {e}')
        return 1


def cmd_repo_list_queues(args: argparse.Namespace) -> int:
    """
    List processing queues command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    queue_manager = QueueManager()
    queues = queue_manager.list_queues(status=args.status)
    
    if not queues:
        print('No queues found.')
        if args.status:
            print(f'Try removing --status filter to see all queues.')
        return 0
    
    print(f'Found {len(queues)} queue(s):')
    print()
    
    for queue in queues:
        print(f'Queue ID: {queue.queue_id}')
        print(f'  Person: {queue.source_person}')
        print(f'  Face ID: {queue.source_face_id}')
        print(f'  Destination: {queue.destination_media}')
        print(f'  Face Selector: {queue.destination_selection.face_selector_mode}')
        print(f'  Status: {queue.status}')
        print(f'  Created: {queue.created_date}')
        print()
    
    return 0


def cmd_repo_queue_stats(args: argparse.Namespace) -> int:
    """
    Show queue statistics command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    queue_manager = QueueManager()
    stats = queue_manager.get_queue_statistics()
    
    print('Queue Statistics:')
    print('-' * 60)
    print(f'Total Queues: {stats["total"]}')
    print()
    
    if stats['by_status']:
        print('By Status:')
        for status, count in sorted(stats['by_status'].items()):
            print(f'  {status}: {count}')
        print()
    
    if stats['by_person']:
        print('By Person:')
        for person, count in sorted(stats['by_person'].items()):
            print(f'  {person}: {count}')
    
    return 0
