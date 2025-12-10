#!/usr/bin/env python3
"""
Example Workflow Script for FaceFusion Repository System

This script demonstrates a complete workflow using the repository system:
1. Initialize repository
2. Add faces at different orientations
3. View repository statistics
4. (Would analyze destination media if we had test files)
5. Show batch processing status
6. (Would run batch processing if we had queues)

This serves as both a demonstration and a test of the system's functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path to import facefusion modules
sys.path.insert(0, str(Path(__file__).parent))

from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.destination.queue_manager import QueueManager


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print()
    print('=' * 70)
    print(f'  {title}')
    print('=' * 70)
    print()


def main() -> int:
    """
    Run the example workflow demonstration.
    
    Returns:
        Exit code (0 for success)
    """
    print_section('FaceFusion Repository System - Example Workflow')
    
    print('This script demonstrates the FaceFusion Repository System workflow.')
    print('It shows how the system manages faces, analyzes orientations, and')
    print('prepares batch processing operations.')
    print()
    
    # Step 1: Check if repository exists
    print_section('Step 1: Repository Status')
    
    repo = RepositoryManager()
    
    if not repo.repository_path.exists():
        print('Repository not initialized.')
        print('Run: python facefusion_repo_cli.py init')
        print()
        print('Then add some faces:')
        print('  python facefusion_repo_cli.py add --source face.jpg --name "Person Name"')
        return 0
    
    print(f'✓ Repository found at: {repo.repository_path}')
    
    # Get repository statistics
    faces = repo.list_faces()
    print(f'✓ Total faces in repository: {len(faces)}')
    
    if len(faces) == 0:
        print()
        print('Repository is empty. Add faces using:')
        print('  python facefusion_repo_cli.py add --source face.jpg --name "Person Name"')
        return 0
    
    # Step 2: Show face details
    print_section('Step 2: Repository Faces')
    
    print('Faces in repository:')
    print()
    
    for face in faces:
        name = face.metadata.name or 'Unnamed'
        orientation = face.orientation_angle
        quality = face.quality_metrics.overall_quality
        
        print(f'  • {face.id}')
        print(f'    Name: {name}')
        print(f'    Orientation: {orientation}°')
        print(f'    Quality: {quality:.2f}')
        print()
    
    # Step 3: Show orientation coverage
    print_section('Step 3: Orientation Coverage')
    
    # Count faces by orientation
    orientation_counts = {}
    for face in faces:
        angle = face.orientation_angle
        orientation_counts[angle] = orientation_counts.get(angle, 0) + 1
    
    all_orientations = [0, 45, 90, 135, 180, 225, 270, 315]
    covered = [angle for angle in all_orientations if angle in orientation_counts]
    missing = [angle for angle in all_orientations if angle not in orientation_counts]
    
    coverage_percent = (len(covered) / len(all_orientations)) * 100
    
    print(f'Coverage: {coverage_percent:.1f}% ({len(covered)}/{len(all_orientations)} orientations)')
    print()
    print('Covered orientations:', ', '.join(f'{a}°' for a in sorted(covered)))
    if missing:
        print('Missing orientations:', ', '.join(f'{a}°' for a in sorted(missing)))
    print()
    
    # Visual representation using helper function
    print_orientation_wheel(covered)
    print()


def print_orientation_wheel(covered: list) -> None:
    """
    Print visual orientation wheel showing covered/missing orientations.
    
    Args:
        covered: List of orientation angles that are covered
    """
    def status(angle: int) -> str:
        return '✓' if angle in covered else '✗'
    
    print('Orientation Wheel:')
    print(f'           0° {status(0)}')
    print('       ┌───┴───┐')
    print(f'    315° {status(315)} │     │ 45° {status(45)}')
    print('   ┌────┤  *  ├────┐')
    print(f'  270° {status(270)}  └─────┘   90° {status(90)}')
    print('       └───┬───┘')
    print(f'          180° {status(180)}')
    
    # Step 4: Check for queues
    print_section('Step 4: Processing Queues')
    
    queue_manager = QueueManager()
    queues = queue_manager.list_queues()
    
    if len(queues) == 0:
        print('No processing queues found.')
        print()
        print('To create queues, analyze destination media:')
        print('  python facefusion_repo_cli.py analyze-destination --source video.mp4')
        print()
    else:
        print(f'✓ Found {len(queues)} processing queue(s)')
        print()
        
        stats = queue_manager.get_statistics()
        print(f'Total faces to process: {stats.total_faces}')
        print()
        
        # Show queue details
        print('Queue Details:')
        print()
        for queue in queues:
            face = repo.get_face(queue.source_face_id)
            # Get face name with explicit null checking for clarity
            if face and face.metadata and face.metadata.name:
                name = face.metadata.name
            else:
                name = 'Unnamed'
            
            print(f'  • {queue.source_face_id} ({name})')
            print(f'    Matches: {queue.get_size()}')
            print(f'    Avg Confidence: {queue.get_average_confidence():.2f}')
            print()
        
        print('Run batch processing with:')
        print('  python facefusion_repo_cli.py batch-run --output ./output --dry-run')
        print()
    
    # Step 5: Summary
    print_section('Summary')
    
    print('Workflow Status:')
    print(f'  ✓ Repository initialized: Yes')
    print(f'  ✓ Faces added: {len(faces)}')
    print(f'  ✓ Orientation coverage: {coverage_percent:.1f}%')
    print(f'  ✓ Processing queues: {len(queues)}')
    print()
    
    if len(queues) > 0:
        print('Ready for batch processing!')
        print('Use: python facefusion_repo_cli.py batch-status')
        print('Then: python facefusion_repo_cli.py batch-run --output ./output')
    else:
        print('Next step: Analyze destination media to create processing queues')
        print('Use: python facefusion_repo_cli.py analyze-destination --source <file>')
    
    print()
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\n\nInterrupted by user')
        sys.exit(1)
    except Exception as e:
        print(f'\nError: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
