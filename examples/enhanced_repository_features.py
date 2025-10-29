#!/usr/bin/env python3
"""
Example script demonstrating the enhanced repository system features.

This script shows how to use:
- Quality assessment during face addition
- Quality-based face selection
- Settings profile management
- Pose-aware selection (API usage)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from facefusion_repository.manager import RepositoryManager
from facefusion_repository.selector import RepositorySelector
from facefusion_repository.settings import SettingsManager
from facefusion_repository.quality_assessor import assess_face_from_path


def example_quality_assessment():
	"""Example: Assess quality of face images."""
	print("\n=== Quality Assessment Example ===")
	
	# Assess a single face
	face_path = "path/to/face.jpg"
	# metrics = assess_face_from_path(face_path)
	# print(f"Quality metrics for {face_path}:")
	# print(f"  Sharpness: {metrics.sharpness:.2f}")
	# print(f"  Brightness: {metrics.brightness:.2f}")
	# print(f"  Contrast: {metrics.contrast:.2f}")
	# print(f"  Resolution: {metrics.resolution:.2f}")
	# print(f"  Overall: {metrics.overall:.2f}")
	
	print("(Requires actual face image file to run)")


def example_quality_filtering():
	"""Example: Add person with quality filtering."""
	print("\n=== Quality Filtering Example ===")
	
	manager = RepositoryManager('.face_repository_example')
	
	# Add person with quality threshold
	# Only faces with quality >= 0.7 will be added
	face_paths = ["face1.jpg", "face2.jpg", "face3.jpg", "face4.jpg"]
	
	print("Adding person with quality threshold of 0.7...")
	# person = manager.create_person(
	#     'high_quality_person',
	#     face_paths,
	#     quality_threshold=0.7,
	#     assess_quality=True
	# )
	# print(f"Added {person['face_count']} high-quality faces")
	
	print("(Requires actual face image files to run)")


def example_quality_based_selection():
	"""Example: Select faces based on quality."""
	print("\n=== Quality-Based Selection Example ===")
	
	manager = RepositoryManager('.face_repository_example')
	selector = RepositorySelector(manager)
	
	# Get best quality face
	print("Selecting best quality face...")
	# best_face = selector.get_best_person_face('person_name', quality_threshold=0.8)
	# print(f"Best face: {best_face}")
	
	# Get all faces above quality threshold, sorted by quality
	print("Getting faces with quality >= 0.7...")
	# faces = selector.get_faces_by_quality('person_name', quality_threshold=0.7, sort_by_quality=True)
	# print(f"Found {len(faces)} faces meeting quality criteria")
	
	print("(Requires existing repository with quality metadata)")


def example_settings_management():
	"""Example: Manage settings profiles."""
	print("\n=== Settings Management Example ===")
	
	settings_manager = SettingsManager('.face_repository_example')
	
	# List built-in templates
	templates = settings_manager.get_builtin_templates()
	print(f"Built-in templates: {', '.join(templates)}")
	
	# Get a built-in profile
	high_quality = settings_manager.get_profile('high_quality')
	if high_quality:
		print("\nHigh Quality Profile Settings:")
		for key, value in high_quality['settings'].items():
			print(f"  {key}: {value}")
	
	# Create a custom profile
	custom_settings = {
		'face_detector_model': 'retinaface',
		'quality_threshold': 0.85,
		'orientation_tolerance': 12.0,
		'face_selector_mode': 'best-quality'
	}
	
	success = settings_manager.create_profile(
		'my_custom_profile',
		custom_settings,
		'My custom high-quality settings'
	)
	
	if success:
		print("\n✓ Created custom profile 'my_custom_profile'")
	
	# List all profiles
	all_profiles = settings_manager.list_profiles()
	print(f"\nAll profiles: {', '.join(all_profiles)}")
	
	# Export profile
	# settings_manager.export_profile('my_custom_profile', 'my_profile.json')
	# print("\n✓ Exported profile to my_profile.json")


def example_pose_aware_selection():
	"""Example: Use pose-aware face selection (API)."""
	print("\n=== Pose-Aware Selection Example ===")
	
	from facefusion_repository.pose_calculator import (
		calculate_pose_similarity,
		is_pose_within_tolerance
	)
	
	# Example poses (pitch, yaw, roll in degrees)
	target_pose = (10.0, 15.0, 5.0)  # Slightly looking up and to the right
	face_pose_1 = (12.0, 14.0, 6.0)  # Very similar
	face_pose_2 = (45.0, 30.0, 10.0)  # Different angle
	
	# Calculate similarity
	similarity_1 = calculate_pose_similarity(target_pose, face_pose_1)
	similarity_2 = calculate_pose_similarity(target_pose, face_pose_2)
	
	print(f"Target pose: {target_pose}")
	print(f"\nFace 1 pose: {face_pose_1}")
	print(f"  Similarity: {similarity_1:.2f}")
	print(f"  Within 15° tolerance: {is_pose_within_tolerance(target_pose, face_pose_1, 15.0)}")
	
	print(f"\nFace 2 pose: {face_pose_2}")
	print(f"  Similarity: {similarity_2:.2f}")
	print(f"  Within 15° tolerance: {is_pose_within_tolerance(target_pose, face_pose_2, 15.0)}")
	
	# Use with selector
	manager = RepositoryManager('.face_repository_example')
	selector = RepositorySelector(manager)
	
	# Get best face matching target pose
	print("\nSelecting face with matching pose...")
	# best_match = selector.get_best_face_by_pose_similarity(
	#     'person_name',
	#     target_pose,
	#     orientation_tolerance=15.0
	# )
	# print(f"Best matching face: {best_match}")
	
	print("(Requires repository with pose metadata)")


def example_cli_commands():
	"""Example: CLI commands for enhanced features."""
	print("\n=== CLI Command Examples ===")
	
	print("\n1. Add person with quality filtering:")
	print("   python facefusion.py repo-add \\")
	print("       --person 'Marie' \\")
	print("       --face-paths face1.jpg face2.jpg face3.jpg \\")
	print("       --quality-threshold 0.7")
	
	print("\n2. Execute with best quality face:")
	print("   python facefusion.py repo-execute \\")
	print("       --person 'Marie' \\")
	print("       --face-selector-mode 'best-quality' \\")
	print("       --quality-threshold 0.8 \\")
	print("       --target video.mp4 \\")
	print("       --output result.mp4 \\")
	print("       --processors face_swapper")
	
	print("\n3. List settings profiles:")
	print("   python facefusion.py repo-settings-list")
	
	print("\n4. Show profile details:")
	print("   python facefusion.py repo-settings-show \\")
	print("       --profile-name 'high_quality'")
	
	print("\n5. Export profile:")
	print("   python facefusion.py repo-settings-export \\")
	print("       --profile-name 'high_quality' \\")
	print("       --settings-file my_settings.json")
	
	print("\n6. Import profile:")
	print("   python facefusion.py repo-settings-import \\")
	print("       --profile-name 'custom_profile' \\")
	print("       --settings-file my_settings.json")


def main():
	"""Run all examples."""
	print("=" * 60)
	print("Enhanced Repository System - Feature Examples")
	print("=" * 60)
	
	example_quality_assessment()
	example_quality_filtering()
	example_quality_based_selection()
	example_settings_management()
	example_pose_aware_selection()
	example_cli_commands()
	
	print("\n" + "=" * 60)
	print("Examples completed!")
	print("=" * 60)


if __name__ == '__main__':
	main()
