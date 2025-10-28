"""
CLI commands for FaceFusion Repository System.
"""

import argparse

from facefusion_repository.repository.compatibility_matrix import CompatibilityMatrix
from facefusion_repository.repository.manager import RepositoryManager


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
        '--name',
        help='Name for the face'
    )
    parser_add.add_argument(
        '--tags',
        help='Comma-separated tags'
    )
    parser_add.set_defaults(func=cmd_repo_add_face)

    # repo-list command
    parser_list = subparsers.add_parser(
        'repo-list',
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
            print(f'  Name: {args.name}')
        if tags:
            print(f'  Tags: {", ".join(tags)}')

        # Show face details
        face = repo.get_face(face_id)
        if face:
            print(f'  Orientation: {face.orientation_angle}°')
            print(f'  Quality: {face.quality_metrics.overall_quality:.2f}')
            print(f'  Resolution: {face.quality_metrics.resolution[0]}x{face.quality_metrics.resolution[1]}')
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

    print(f'Found {len(faces)} face(s):')
    print()

    for face in faces:
        print(f'ID: {face.id}')
        print(f'  Name: {face.metadata.name or "Unnamed"}')
        print(f'  Orientation: {face.orientation_angle}°')
        print(f'  Quality: {face.quality_metrics.overall_quality:.2f}')
        print(f'  Resolution: {face.quality_metrics.resolution[0]}x{face.quality_metrics.resolution[1]}')
        if face.metadata.tags:
            print(f'  Tags: {", ".join(face.metadata.tags)}')
        print(f'  Added: {face.metadata.added_date}')
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

    print(f'Face Details: {args.face_id}')
    print('=' * 60)
    print()
    print(f'Name: {face.metadata.name or "Unnamed"}')
    print(f'File: {face.file_path}')
    print(f'Orientation: {face.orientation_angle}°')
    print()
    print('Quality Metrics:')
    print(f'  Resolution: {face.quality_metrics.resolution[0]}x{face.quality_metrics.resolution[1]}')
    print(f'  Sharpness: {face.quality_metrics.sharpness:.3f}')
    print(f'  Brightness: {face.quality_metrics.brightness:.3f}')
    print(f'  Contrast: {face.quality_metrics.contrast:.3f}')
    print(f'  Detector Score: {face.quality_metrics.detector_score:.3f}')
    print(f'  Overall Quality: {face.quality_metrics.overall_quality:.3f}')
    print()
    if face.metadata.tags:
        print(f'Tags: {", ".join(face.metadata.tags)}')
    print(f'Added: {face.metadata.added_date}')

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
