"""
CLI commands for FaceFusion Repository System with person-based architecture.
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

    # repo-add-person command (NEW)
    parser_add_person = subparsers.add_parser(
        'repo-add-person',
        help='Add a new person to the repository'
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
    parser_add_person.set_defaults(func=cmd_repo_add_person)

    # repo-people command (NEW)
    parser_people = subparsers.add_parser(
        'repo-people',
        help='List all people in the repository'
    )
    parser_people.set_defaults(func=cmd_repo_people)

    # repo-add-face command (UPDATED to require --person)
    parser_add = subparsers.add_parser(
        'repo-add-face',
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
    parser_add.set_defaults(func=cmd_repo_add_face)

    # repo-list command (UPDATED to support --person filter)
    parser_list = subparsers.add_parser(
        'repo-list',
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


def cmd_repo_add_person(args: argparse.Namespace) -> int:
    """
    Add person to repository command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    person_id = args.person
    display_name = args.display_name or person_id

    print(f'Adding person: {person_id}')

    repo = RepositoryManager()
    if repo.add_person(person_id, display_name):
        print(f'✓ Person added successfully!')
        print(f'  ID: {person_id}')
        print(f'  Display Name: {display_name}')
        print(f'  Directory: {repo.faces_dir / person_id}')
        return 0
    else:
        print('✗ Failed to add person (see error messages above)')
        return 1


def cmd_repo_people(args: argparse.Namespace) -> int:
    """
    List people in repository command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    repo = RepositoryManager()
    people = repo.list_people()

    if not people:
        print('No people in repository.')
        print('Use "repo-add-person" to add a person first.')
        return 0

    print(f'People in repository: {len(people)}')
    print()

    for person in people:
        print(f'  Person: {person.id}')
        print(f'    Display Name: {person.display_name}')
        print(f'    Faces: {len(person.face_ids)}')
        print(f'    Created: {person.created_date}')
        print(f'    Last Modified: {person.last_modified}')
        print()

    return 0


def cmd_repo_init(args: argparse.Namespace) -> int:
    """
    Initialize repository command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    print('Initializing FaceFusion Repository (Person-Based Architecture)...')

    repo = RepositoryManager()

    if repo.initialize_repository():
        print('✓ Repository initialized successfully at {}'.format(repo.repository_path))
        print('  Structure:')
        print('    - faces/         (Person-based face storage)')
        print('    - settings/      (FaceFusion settings profiles)')
        print('    - presets/       (Person + settings presets)')
        print('    - queues/        (Processing queues)')
        print('    - test_images/   (Preview reference images)')
        return 0
    else:
        print('✗ Failed to initialize repository')
        return 1


def cmd_repo_add_face(args: argparse.Namespace) -> int:
    """
    Add face to repository command (person-based).

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    print(f'Adding face from: {args.source}')
    print(f'For person: {args.person}')

    # Parse tags if provided
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]

    repo = RepositoryManager()
    face_id = repo.add_face(
        image_path=args.source,
        person_id=args.person,
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
    List faces in repository command (with person filter).

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    # Parse tags if provided
    filter_tags = None
    if hasattr(args, 'tags') and args.tags:
        filter_tags = [tag.strip() for tag in args.tags.split(',')]

    repo = RepositoryManager()
    faces = repo.list_faces(
        filter_by_orientation=getattr(args, 'orientation', None),
        filter_by_tags=filter_tags
    )

    # Apply person filter if specified
    if hasattr(args, 'person') and args.person:
        faces = [f for f in faces if f.metadata.person_id == args.person]

    if not faces:
        print('No faces found in repository.')
        if hasattr(args, 'orientation') and args.orientation or filter_tags or (hasattr(args, 'person') and args.person):
            print('Try removing filters to see all faces.')
        else:
            print('Use "repo-add-face --person <person> --source <image>" to add faces.')
        return 0

    print('Found {} face(s):'.format(len(faces)))
    print()

    # Group faces by person for better display
    faces_by_person = {}
    for face in faces:
        person_id = face.metadata.person_id
        if person_id not in faces_by_person:
            faces_by_person[person_id] = []
        faces_by_person[person_id].append(face)

    for person_id, person_faces in sorted(faces_by_person.items()):
        print(f'Person: {person_id} ({len(person_faces)} faces)')
        for face in person_faces:
            print('  ID: {}'.format(face.id))
            print('    Name: {}'.format(face.metadata.name or 'Unnamed'))
            print('    Orientation: {}°'.format(face.orientation_angle))
            print('    Quality: {:.2f}'.format(face.quality_metrics.overall_quality))
            print('    Resolution: {}x{}'.format(face.quality_metrics.resolution[0], face.quality_metrics.resolution[1]))
            if face.metadata.tags:
                print('    Tags: {}'.format(', '.join(face.metadata.tags)))
            print('    Added: {}'.format(face.metadata.added_date))
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
    Show repository statistics command (person-based).

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    repo = RepositoryManager()
    stats = repo.get_statistics()

    if stats is None:
        print('✗ Failed to get repository statistics')
        return 1

    print('Repository Statistics')
    print('=' * 60)
    print()
    print('Total People: {}'.format(stats.total_people))
    print('Total Faces: {}'.format(stats.total_faces))
    print('Average Quality: {:.2f}'.format(stats.average_quality))
    print('Storage Used: {:.2f} MB'.format(stats.total_size_mb))
    print()

    # Show faces by person
    if stats.faces_by_person:
        print('Faces by Person:')
        for person_id, count in sorted(stats.faces_by_person.items()):
            print('  {}: {} faces'.format(person_id, count))
        print()

    # Show compatibility matrix
    matrix = CompatibilityMatrix(repo)
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
