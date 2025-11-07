#!/usr/bin/env python3
"""
Example script demonstrating import preview and zone-specific face management.

This script shows how to use:
- Import preview on test faces
- Zone-specific coverage management
- Overlap resolution
- Test faces management
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import modules (may fail in test environment without dependencies)
try:
	from facefusion_repository.manager import RepositoryManager
	from facefusion_repository.preview import generate_import_preview, compare_overlap_previews
	from facefusion_repository.test_faces import (
		create_test_faces_directory,
		get_test_faces,
		add_test_face
	)
	from facefusion_repository.zone_manager import (
		calculate_zone_from_orientation,
		check_zone_overlap,
		format_zone_description
	)
	IMPORTS_AVAILABLE = True
except ImportError as e:
	print(f"Warning: Could not import some modules: {e}")
	print("This is expected in test environments without full dependencies.")
	print("The examples will show API usage without actual execution.\n")
	IMPORTS_AVAILABLE = False


def example_test_faces_setup():
	"""Example: Set up test faces directory."""
	print("\n=== Test Faces Setup Example ===")
	
	if not IMPORTS_AVAILABLE:
		print("(Showing API example - imports not available)")
		print("\nfrom facefusion_repository.test_faces import create_test_faces_directory")
		print("test_dir = create_test_faces_directory('./test_faces')")
		return
	
	# Create test faces directory
	test_dir = create_test_faces_directory('./test_faces')
	print(f"Created test faces directory: {test_dir}")
	print(f"Please add test face images to this directory")
	print(f"Recommended: front, profile_left, profile_right, looking_up, looking_down")
	
	# Add a test face (if you have one)
	# add_test_face('path/to/your/test_face.jpg', './test_faces')


def example_import_preview():
	"""Example: Preview face import on test faces."""
	print("\n=== Import Preview Example ===")
	
	if not IMPORTS_AVAILABLE:
		print("(Showing API example - imports not available)")
		print("\nfrom facefusion_repository.preview import generate_import_preview")
		print("preview_results = generate_import_preview(source_face, test_faces)")
		return
	
	# Get test faces
	test_faces = get_test_faces('./test_faces')
	
	if not test_faces:
		print("No test faces found. Please add test faces first.")
		return
	
	print(f"Found {len(test_faces)} test faces")
	
	# Simulate face import preview
	source_face = 'path/to/new_face.jpg'
	
	print(f"\nGenerating preview for: {source_face}")
	print("(Note: This requires valid face images)")
	
	# In a real scenario:
	# preview_results = generate_import_preview(source_face, test_faces)
	# 
	# for test_face, result in preview_results.items():
	#     print(f"\nTest face: {Path(test_face).name}")
	#     print(f"  Success: {result.success}")
	#     print(f"  Quality: {result.quality_score:.2f}")
	#     print(f"  Preview: {result.preview_path}")


def example_overlap_comparison():
	"""Example: Compare faces for overlap resolution."""
	print("\n=== Overlap Comparison Example ===")
	
	if not IMPORTS_AVAILABLE:
		print("(Showing API example - imports not available)")
		print("\nfrom facefusion_repository.preview import compare_overlap_previews")
		print("comparison_results = compare_overlap_previews(existing, new, test_faces)")
		return
	
	test_faces = get_test_faces('./test_faces')
	
	if not test_faces:
		print("No test faces found. Please add test faces first.")
		return
	
	existing_face = 'path/to/existing_face.jpg'
	new_face = 'path/to/new_face.jpg'
	
	print(f"\nComparing faces:")
	print(f"  Existing: {existing_face}")
	print(f"  New: {new_face}")
	print("(Note: This requires valid face images)")
	
	# In a real scenario:
	# comparison_results = compare_overlap_previews(
	#     existing_face,
	#     new_face,
	#     test_faces
	# )
	# 
	# for test_face, comp_result in comparison_results.items():
	#     print(f"\nTest face: {Path(test_face).name}")
	#     print(f"  Existing quality: {comp_result.existing_preview.quality_score:.2f}")
	#     print(f"  New quality: {comp_result.new_preview.quality_score:.2f}")
	#     print(f"  Winner: {comp_result.winner}")


def example_zone_management():
	"""Example: Zone management and overlap detection."""
	print("\n=== Zone Management Example ===")
	
	if not IMPORTS_AVAILABLE:
		print("(Showing API example - imports not available)")
		print("\nfrom facefusion_repository.zone_manager import (")
		print("    calculate_zone_from_orientation,")
		print("    check_zone_overlap,")
		print("    format_zone_description")
		print(")")
		print("\nzone = calculate_zone_from_orientation(orientation, tolerance=15.0)")
		print("overlap = check_zone_overlap(zone1, zone2)")
		return
	
	# Define face orientations
	face1_orientation = {'pitch': 10.0, 'yaw': 20.0, 'roll': 5.0}
	face2_orientation = {'pitch': 12.0, 'yaw': 22.0, 'roll': 6.0}  # Similar
	face3_orientation = {'pitch': 45.0, 'yaw': 30.0, 'roll': 10.0}  # Different
	
	# Calculate coverage zones
	tolerance = 15.0
	zone1 = calculate_zone_from_orientation(face1_orientation, tolerance)
	zone2 = calculate_zone_from_orientation(face2_orientation, tolerance)
	zone3 = calculate_zone_from_orientation(face3_orientation, tolerance)
	
	print("\nFace 1 orientation:", face1_orientation)
	print("Coverage zone:", format_zone_description(zone1))
	
	print("\nFace 2 orientation:", face2_orientation)
	print("Coverage zone:", format_zone_description(zone2))
	
	print("\nFace 3 orientation:", face3_orientation)
	print("Coverage zone:", format_zone_description(zone3))
	
	# Check overlaps
	overlap_1_2 = check_zone_overlap(zone1, zone2)
	overlap_1_3 = check_zone_overlap(zone1, zone3)
	
	print(f"\nZone overlap between Face 1 and Face 2: {overlap_1_2}")
	print(f"Zone overlap between Face 1 and Face 3: {overlap_1_3}")
	
	if overlap_1_2:
		print("  → Faces 1 and 2 have overlapping zones (conflict)")
		print("  → Resolution: Compare quality and choose best for this zone")
	
	if not overlap_1_3:
		print("  → Faces 1 and 3 have non-overlapping zones (good coverage)")
		print("  → Both faces can coexist in repository")


def example_manager_preview():
	"""Example: Using manager's preview methods."""
	print("\n=== Manager Preview Methods Example ===")
	
	print("\nPreview face import:")
	print("  manager = RepositoryManager('.face_repository')")
	print("  result = manager.preview_face_import(")
	print("      'new_face.jpg',")
	print("      test_faces_dir='./test_faces',")
	print("      max_test_faces=5")
	print("  )")
	
	print("\nCompare faces on test cases:")
	print("  comparison = manager.compare_faces_on_test_cases(")
	print("      'existing_face.jpg',")
	print("      'new_face.jpg',")
	print("      test_faces_dir='./test_faces'")
	print("  )")


def example_cli_commands():
	"""Example: CLI commands for preview features."""
	print("\n=== CLI Command Examples ===")
	
	print("\n1. Add face with preview:")
	print("   python facefusion.py repo-add \\")
	print("       --person 'Marie' \\")
	print("       --face-paths new_face.jpg \\")
	print("       --preview-on-test-faces \\")
	print("       --test-faces-dir ./test_faces")
	
	print("\n2. Add face with preview and quality threshold:")
	print("   python facefusion.py repo-add \\")
	print("       --person 'Marie' \\")
	print("       --face-paths new_face.jpg \\")
	print("       --preview-on-test-faces \\")
	print("       --quality-threshold 0.7 \\")
	print("       --test-faces-dir ./test_faces")
	
	print("\n3. Add face with interactive mode:")
	print("   python facefusion.py repo-add \\")
	print("       --person 'Marie' \\")
	print("       --face-paths new_face.jpg \\")
	print("       --preview-on-test-faces \\")
	print("       --interactive")


def main():
	"""Run all examples."""
	print("=" * 70)
	print("Import Preview and Zone-Specific Face Management - Examples")
	print("=" * 70)
	
	example_test_faces_setup()
	example_import_preview()
	example_overlap_comparison()
	example_zone_management()
	example_manager_preview()
	example_cli_commands()
	
	print("\n" + "=" * 70)
	print("Examples completed!")
	print("=" * 70)
	print("\nNOTE: Most examples require actual face images to run.")
	print("The examples demonstrate the API structure and expected usage.")


if __name__ == '__main__':
	main()
