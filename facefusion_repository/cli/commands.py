"""
CLI commands for FaceFusion Repository System.
"""

import argparse
import json

from facefusion_repository.presets.applicator import PresetApplicator
from facefusion_repository.presets.collection import PresetCollection
from facefusion_repository.presets.manager import PresetManager
from facefusion_repository.presets.template import PresetTemplate
from facefusion_repository.repository.compatibility_matrix import CompatibilityMatrix
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.manager import SettingsManager


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


def register_settings_commands(subparsers: argparse._SubParsersAction) -> None:
    """
    Register settings management commands.

    Args:
        subparsers: Subparser object from argparse
    """
    # settings-create command
    parser_create = subparsers.add_parser(
        'settings-create',
        help='Create settings profile'
    )
    parser_create.add_argument('--name', required=True, help='Profile name')
    parser_create.add_argument('--file', help='JSON file with settings')
    parser_create.add_argument('--template', help='Use template (high_quality, fast_processing, etc.)')
    parser_create.add_argument('--description', help='Profile description')
    parser_create.set_defaults(func=cmd_settings_create)

    # settings-list command
    parser_list = subparsers.add_parser(
        'settings-list',
        help='List settings profiles'
    )
    parser_list.set_defaults(func=cmd_settings_list)

    # settings-show command
    parser_show = subparsers.add_parser(
        'settings-show',
        help='Show settings profile'
    )
    parser_show.add_argument('--name', required=True, help='Profile name')
    parser_show.set_defaults(func=cmd_settings_show)

    # settings-delete command
    parser_delete = subparsers.add_parser(
        'settings-delete',
        help='Delete settings profile'
    )
    parser_delete.add_argument('--name', required=True, help='Profile name')
    parser_delete.set_defaults(func=cmd_settings_delete)

    # settings-export command
    parser_export = subparsers.add_parser(
        'settings-export',
        help='Export settings profile'
    )
    parser_export.add_argument('--name', required=True, help='Profile name')
    parser_export.add_argument('--output', required=True, help='Output file path')
    parser_export.set_defaults(func=cmd_settings_export)

    # settings-import command
    parser_import = subparsers.add_parser(
        'settings-import',
        help='Import settings profile'
    )
    parser_import.add_argument('--file', required=True, help='Input file path')
    parser_import.add_argument('--name', help='New profile name')
    parser_import.set_defaults(func=cmd_settings_import)


def register_presets_commands(subparsers: argparse._SubParsersAction) -> None:
    """
    Register preset management commands.

    Args:
        subparsers: Subparser object from argparse
    """
    # presets-create command
    parser_create = subparsers.add_parser(
        'presets-create',
        help='Create new preset'
    )
    parser_create.add_argument('--name', required=True, help='Preset name')
    parser_create.add_argument('--face-id', required=True, help='Face ID from repository')
    parser_create.add_argument('--settings', required=True, help='Settings profile name')
    parser_create.add_argument('--description', help='Preset description')
    parser_create.add_argument('--tags', help='Comma-separated tags')
    parser_create.set_defaults(func=cmd_presets_create)

    # presets-list command
    parser_list = subparsers.add_parser(
        'presets-list',
        help='List all presets'
    )
    parser_list.add_argument('--face-id', help='Filter by face ID')
    parser_list.add_argument('--settings', help='Filter by settings profile')
    parser_list.set_defaults(func=cmd_presets_list)

    # presets-show command
    parser_show = subparsers.add_parser(
        'presets-show',
        help='Show preset details'
    )
    parser_show.add_argument('--name', required=True, help='Preset name')
    parser_show.set_defaults(func=cmd_presets_show)

    # presets-update command
    parser_update = subparsers.add_parser(
        'presets-update',
        help='Update existing preset'
    )
    parser_update.add_argument('--name', required=True, help='Preset name')
    parser_update.add_argument('--face-id', help='New face ID')
    parser_update.add_argument('--settings', help='New settings profile')
    parser_update.add_argument('--description', help='New description')
    parser_update.set_defaults(func=cmd_presets_update)

    # presets-delete command
    parser_delete = subparsers.add_parser(
        'presets-delete',
        help='Delete preset'
    )
    parser_delete.add_argument('--name', required=True, help='Preset name')
    parser_delete.set_defaults(func=cmd_presets_delete)

    # presets-validate command
    parser_validate = subparsers.add_parser(
        'presets-validate',
        help='Validate preset'
    )
    parser_validate.add_argument('--name', required=True, help='Preset name')
    parser_validate.set_defaults(func=cmd_presets_validate)

    # presets-copy command
    parser_copy = subparsers.add_parser(
        'presets-copy',
        help='Copy preset'
    )
    parser_copy.add_argument('--source', required=True, help='Source preset name')
    parser_copy.add_argument('--name', required=True, help='New preset name')
    parser_copy.add_argument('--face-id', help='Override face ID')
    parser_copy.add_argument('--settings', help='Override settings profile')
    parser_copy.set_defaults(func=cmd_presets_copy)

    # presets-export command
    parser_export = subparsers.add_parser(
        'presets-export',
        help='Export preset'
    )
    parser_export.add_argument('--name', required=True, help='Preset name')
    parser_export.add_argument('--output', required=True, help='Output file path')
    parser_export.set_defaults(func=cmd_presets_export)

    # presets-import command
    parser_import = subparsers.add_parser(
        'presets-import',
        help='Import preset'
    )
    parser_import.add_argument('--file', required=True, help='Input file path')
    parser_import.add_argument('--name', help='New preset name')
    parser_import.set_defaults(func=cmd_presets_import)

    # presets-apply command
    parser_apply = subparsers.add_parser(
        'presets-apply',
        help='Show preset configuration for application'
    )
    parser_apply.add_argument('--name', required=True, help='Preset name')
    parser_apply.set_defaults(func=cmd_presets_apply)


# Settings command implementations

def cmd_settings_create(args: argparse.Namespace) -> int:
    """Create settings profile."""
    manager = SettingsManager()

    # Load settings from file or template
    settings = {}
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                settings = data.get('settings', data)
        except Exception as e:
            print(f'✗ Error loading settings file: {e}')
            return 1
    elif args.template:
        template_settings = PresetTemplate.get_template(args.template)
        if template_settings is None:
            print(f'✗ Unknown template: {args.template}')
            print(f'Available templates: {", ".join(PresetTemplate.list_templates())}')
            return 1
        settings = template_settings
    else:
        print('✗ Either --file or --template must be specified')
        return 1

    if manager.create_profile(args.name, settings, args.description):
        print(f'✓ Created settings profile: {args.name}')
        return 0
    return 1


def cmd_settings_list(args: argparse.Namespace) -> int:
    """List settings profiles."""
    manager = SettingsManager()
    profiles = manager.list_profiles()

    if not profiles:
        print('No settings profiles found.')
        print('Create one with: settings-create --name <name> --template high_quality')
        return 0

    print(f'Found {len(profiles)} settings profile(s):')
    print()

    for name in profiles:
        profile = manager.get_profile(name)
        if profile:
            print(f'Name: {name}')
            print(f'  Description: {profile.get("description", "No description")}')
            print(f'  Created: {profile.get("created_date", "Unknown")}')
            settings = profile.get('settings', {})
            print(f'  Processors: {", ".join(settings.get("processors", []))}')
            print()

    return 0


def cmd_settings_show(args: argparse.Namespace) -> int:
    """Show settings profile."""
    manager = SettingsManager()
    profile = manager.get_profile(args.name)

    if profile is None:
        print(f'✗ Settings profile not found: {args.name}')
        return 1

    print(f'Settings Profile: {args.name}')
    print('=' * 60)
    print()
    print(f'Description: {profile.get("description", "No description")}')
    print(f'Version: {profile.get("version", "Unknown")}')
    print(f'Created: {profile.get("created_date", "Unknown")}')
    print()
    print('Settings:')
    print(json.dumps(profile.get('settings', {}), indent=2))

    return 0


def cmd_settings_delete(args: argparse.Namespace) -> int:
    """Delete settings profile."""
    manager = SettingsManager()
    if manager.delete_profile(args.name):
        print(f'✓ Deleted settings profile: {args.name}')
        return 0
    return 1


def cmd_settings_export(args: argparse.Namespace) -> int:
    """Export settings profile."""
    manager = SettingsManager()
    if manager.export_profile(args.name, args.output):
        return 0
    return 1


def cmd_settings_import(args: argparse.Namespace) -> int:
    """Import settings profile."""
    manager = SettingsManager()
    if manager.import_profile(args.file, args.name):
        return 0
    return 1


# Presets command implementations

def cmd_presets_create(args: argparse.Namespace) -> int:
    """Create new preset."""
    manager = PresetManager()

    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]

    if manager.create_preset(
        name=args.name,
        face_id=args.face_id,
        settings_profile=args.settings,
        description=args.description,
        tags=tags
    ):
        print(f'✓ Created preset: {args.name}')
        return 0
    return 1


def cmd_presets_list(args: argparse.Namespace) -> int:
    """List all presets."""
    manager = PresetManager()
    presets = manager.list_presets(
        filter_by_face_id=args.face_id,
        filter_by_settings=args.settings
    )

    if not presets:
        print('No presets found.')
        print('Create one with: presets-create --name <name> --face-id <id> --settings <profile>')
        return 0

    print(f'Found {len(presets)} preset(s):')
    print()

    for preset in presets:
        print(f'Name: {preset.name}')
        print(f'  Description: {preset.description}')
        print(f'  Face ID: {preset.face_id}')
        print(f'  Settings: {preset.settings_profile}')
        print(f'  Usage Count: {preset.usage_count}')
        if preset.last_used:
            print(f'  Last Used: {preset.last_used}')
        print()

    return 0


def cmd_presets_show(args: argparse.Namespace) -> int:
    """Show preset details."""
    applicator = PresetApplicator()
    summary = applicator.get_preset_summary(args.name)

    if summary is None:
        print(f'✗ Preset not found: {args.name}')
        return 1

    print(summary)
    return 0


def cmd_presets_update(args: argparse.Namespace) -> int:
    """Update existing preset."""
    manager = PresetManager()

    if manager.update_preset(
        name=args.name,
        face_id=args.face_id,
        settings_profile=args.settings,
        description=args.description
    ):
        print(f'✓ Updated preset: {args.name}')
        return 0
    return 1


def cmd_presets_delete(args: argparse.Namespace) -> int:
    """Delete preset."""
    manager = PresetManager()
    if manager.delete_preset(args.name):
        return 0
    return 1


def cmd_presets_validate(args: argparse.Namespace) -> int:
    """Validate preset."""
    applicator = PresetApplicator()
    if applicator.validate_preset_before_apply(args.name):
        print(f'✓ Preset is valid: {args.name}')
        return 0
    return 1


def cmd_presets_copy(args: argparse.Namespace) -> int:
    """Copy preset."""
    manager = PresetManager()

    kwargs = {}
    if args.face_id:
        kwargs['face_id'] = args.face_id
    if args.settings:
        kwargs['settings_profile'] = args.settings

    if manager.copy_preset(args.source, args.name, **kwargs):
        print(f'✓ Copied preset from {args.source} to {args.name}')
        return 0
    return 1


def cmd_presets_export(args: argparse.Namespace) -> int:
    """Export preset."""
    manager = PresetManager()
    if manager.export_preset(args.name, args.output):
        return 0
    return 1


def cmd_presets_import(args: argparse.Namespace) -> int:
    """Import preset."""
    manager = PresetManager()
    if manager.import_preset(args.file, args.name):
        return 0
    return 1


def cmd_presets_apply(args: argparse.Namespace) -> int:
    """Show preset configuration for application."""
    applicator = PresetApplicator()
    config = applicator.apply_preset(args.name)

    if config is None:
        print(f'✗ Failed to apply preset: {args.name}')
        return 1

    print(f'Preset Configuration: {args.name}')
    print('=' * 60)
    print()
    print(f'Face Path: {config["face_path"]}')
    print(f'Settings Profile: {config["settings_profile"]}')
    print()
    print('Metadata:')
    print(json.dumps(config['metadata'], indent=2))
    print()
    print('Settings:')
    print(json.dumps(config['settings'], indent=2))

    return 0
