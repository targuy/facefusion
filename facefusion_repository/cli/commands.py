"""
CLI commands for FaceFusion Repository System.
"""

import argparse
import json

from facefusion_repository.repository.compatibility_matrix import CompatibilityMatrix
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.comparator import ProfileComparator
from facefusion_repository.settings.manager import SettingsManager
from facefusion_repository.settings.template import SettingsTemplate
from facefusion_repository.settings.validator import ProfileValidator


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


# Settings Management Commands

def cmd_settings_create(args: argparse.Namespace) -> int:
    """
    Create settings profile command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()

    # Get settings from template or custom JSON
    if args.template:
        templates = SettingsTemplate.get_all_templates()
        if args.template not in templates:
            print(f'✗ Unknown template: {args.template}')
            print(f'Available templates: {", ".join(templates.keys())}')
            return 1
        settings = templates[args.template]
        description = SettingsTemplate.get_template_descriptions()[args.template]
    elif args.settings_file:
        try:
            with open(args.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            description = args.description or f'Imported from {args.settings_file}'
        except Exception as e:
            print(f'✗ Error reading settings file: {e}')
            return 1
    else:
        print('✗ Either --template or --settings-file must be provided')
        return 1

    # Override description if provided
    if args.description:
        description = args.description

    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]

    # Validate settings
    validation = ProfileValidator.validate_settings(settings)
    if not validation.valid:
        print('✗ Settings validation failed:')
        for error in validation.errors:
            print(f'  - {error}')
        return 1

    if validation.warnings:
        print('⚠ Warnings:')
        for warning in validation.warnings:
            print(f'  - {warning}')
        print()

    # Create profile
    if settings_manager.create_profile(args.name, settings, description, tags):
        return 0
    else:
        return 1


def cmd_settings_list(args: argparse.Namespace) -> int:
    """
    List settings profiles command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()

    # Parse tags filter
    filter_tags = None
    if args.tags:
        filter_tags = [tag.strip() for tag in args.tags.split(',')]

    profiles = settings_manager.list_profiles(filter_by_tags=filter_tags)

    if not profiles:
        print('No settings profiles found.')
        if filter_tags:
            print('Try removing filters to see all profiles.')
        return 0

    print(f'Found {len(profiles)} profile(s):')
    print()

    for profile in profiles:
        print(f'Name: {profile.name}')
        print(f'  Description: {profile.description}')
        print(f'  Created: {profile.created_date}')
        print(f'  Modified: {profile.modified_date}')
        print(f'  Settings: {len(profile.settings)} parameters')
        if profile.tags:
            print(f'  Tags: {", ".join(profile.tags)}')
        print()

    return 0


def cmd_settings_show(args: argparse.Namespace) -> int:
    """
    Show settings profile command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()
    profile = settings_manager.get_profile(args.name)

    if not profile:
        print(f'✗ Profile not found: {args.name}')
        return 1

    print(f'Profile: {profile.name}')
    print('=' * 70)
    print()
    print(f'Description: {profile.description}')
    print(f'Version: {profile.version}')
    print(f'Created: {profile.created_date}')
    print(f'Modified: {profile.modified_date}')
    if profile.tags:
        print(f'Tags: {", ".join(profile.tags)}')
    print()
    print('Settings:')
    print('-' * 70)

    for key, value in sorted(profile.settings.items()):
        print(f'  {key}: {value}')

    return 0


def cmd_settings_update(args: argparse.Namespace) -> int:
    """
    Update settings profile command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()

    # Get new settings if provided
    settings = None
    if args.settings_file:
        try:
            with open(args.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Validate settings
            validation = ProfileValidator.validate_settings(settings)
            if not validation.valid:
                print('✗ Settings validation failed:')
                for error in validation.errors:
                    print(f'  - {error}')
                return 1
        except Exception as e:
            print(f'✗ Error reading settings file: {e}')
            return 1

    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]

    if settings_manager.update_profile(args.name, settings, args.description, tags):
        return 0
    else:
        return 1


def cmd_settings_delete(args: argparse.Namespace) -> int:
    """
    Delete settings profile command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()

    if settings_manager.delete_profile(args.name):
        return 0
    else:
        return 1


def cmd_settings_compare(args: argparse.Namespace) -> int:
    """
    Compare settings profiles command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()

    profile1 = settings_manager.get_profile(args.profile1)
    if not profile1:
        print(f'✗ Profile not found: {args.profile1}')
        return 1

    profile2 = settings_manager.get_profile(args.profile2)
    if not profile2:
        print(f'✗ Profile not found: {args.profile2}')
        return 1

    comparison = ProfileComparator.compare_profiles(profile1, profile2)
    print(ProfileComparator.format_comparison(comparison))

    # Show critical differences
    critical = ProfileComparator.highlight_critical_differences(comparison)
    if critical:
        print('Critical Differences:')
        print('-' * 70)
        for diff in critical:
            print(f'  ⚠ {diff}')
        print()

    return 0


def cmd_settings_export(args: argparse.Namespace) -> int:
    """
    Export settings profile command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()

    if settings_manager.export_profile(args.name, args.output):
        return 0
    else:
        return 1


def cmd_settings_import(args: argparse.Namespace) -> int:
    """
    Import settings profile command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()

    if settings_manager.import_profile(args.input, args.name):
        return 0
    else:
        return 1


def cmd_settings_validate(args: argparse.Namespace) -> int:
    """
    Validate settings profile command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    settings_manager = SettingsManager()
    profile = settings_manager.get_profile(args.name)

    if not profile:
        print(f'✗ Profile not found: {args.name}')
        return 1

    validation = ProfileValidator.validate_settings(profile.settings)

    if validation.valid:
        print(f'✓ Profile "{args.name}" is valid')
        if validation.warnings:
            print('\n⚠ Warnings:')
            for warning in validation.warnings:
                print(f'  - {warning}')
        return 0
    else:
        print(f'✗ Profile "{args.name}" has validation errors:')
        for error in validation.errors:
            print(f'  - {error}')
        if validation.warnings:
            print('\n⚠ Warnings:')
            for warning in validation.warnings:
                print(f'  - {warning}')
        return 1


def cmd_settings_templates(args: argparse.Namespace) -> int:
    """
    List available settings templates command.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    templates = SettingsTemplate.get_all_templates()
    descriptions = SettingsTemplate.get_template_descriptions()

    print('Available Settings Templates:')
    print('=' * 70)
    print()

    for name, settings in templates.items():
        print(f'Template: {name}')
        print(f'  Description: {descriptions[name]}')
        print(f'  Settings: {len(settings)} parameters')
        print()

    print('Use "settings create --name <profile_name> --template <template>" to create from template')
    return 0
