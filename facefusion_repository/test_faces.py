"""Test face management for preview generation."""

import os
from pathlib import Path
from typing import List, Optional


DEFAULT_TEST_FACES_DIR = 'test_faces'


def get_test_faces_directory(custom_dir: Optional[str] = None) -> Path:
	"""
	Get test faces directory path.
	
	Args:
		custom_dir: Optional custom directory path
	
	Returns:
		Path to test faces directory
	"""
	if custom_dir:
		return Path(custom_dir)
	
	# Check in repository directory
	if Path(DEFAULT_TEST_FACES_DIR).exists():
		return Path(DEFAULT_TEST_FACES_DIR)
	
	# Check in user home directory
	home_dir = Path.home() / '.facefusion' / DEFAULT_TEST_FACES_DIR
	if home_dir.exists():
		return home_dir
	
	# Return default path (may not exist yet)
	return Path(DEFAULT_TEST_FACES_DIR)


def get_test_faces(
	test_faces_dir: Optional[str] = None,
	max_count: int = 5
) -> List[str]:
	"""
	Get list of test face image paths.
	
	Args:
		test_faces_dir: Optional directory containing test faces
		max_count: Maximum number of test faces to return
	
	Returns:
		List of test face image paths
	"""
	test_dir = get_test_faces_directory(test_faces_dir)
	
	if not test_dir.exists():
		return []
	
	# Get all image files
	image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
	test_faces = []
	
	for file_path in test_dir.iterdir():
		if file_path.is_file() and file_path.suffix.lower() in image_extensions:
			test_faces.append(str(file_path))
			if len(test_faces) >= max_count:
				break
	
	return sorted(test_faces)


def create_test_faces_directory(directory: Optional[str] = None) -> Path:
	"""
	Create test faces directory if it doesn't exist.
	
	Args:
		directory: Optional directory path to create
	
	Returns:
		Path to created directory
	"""
	test_dir = get_test_faces_directory(directory)
	test_dir.mkdir(parents=True, exist_ok=True)
	
	# Create a README file
	readme_path = test_dir / 'README.md'
	if not readme_path.exists():
		readme_content = """# Test Faces for Preview

This directory contains test face images used for generating previews when importing faces to the repository.

## Usage

Place face images with various orientations in this directory:
- front_face.jpg - Frontal face view
- profile_left.jpg - Left profile view
- profile_right.jpg - Right profile view
- looking_up.jpg - Face looking upward
- looking_down.jpg - Face looking downward

These test faces will be used to preview face swaps before committing faces to the repository.

## Recommendations

- Use diverse orientations (pitch, yaw, roll)
- Use good quality images (sharp, well-lit)
- Use images representative of your typical use cases
- 5-10 test faces are usually sufficient
"""
		readme_path.write_text(readme_content)
	
	return test_dir


def add_test_face(face_path: str, test_faces_dir: Optional[str] = None) -> bool:
	"""
	Add a test face to the test faces directory.
	
	Args:
		face_path: Path to face image to add
		test_faces_dir: Optional custom test faces directory
	
	Returns:
		True if successful, False otherwise
	"""
	import shutil
	
	if not Path(face_path).exists():
		return False
	
	test_dir = get_test_faces_directory(test_faces_dir)
	create_test_faces_directory(str(test_dir))
	
	dest_path = test_dir / Path(face_path).name
	shutil.copy2(face_path, dest_path)
	
	return True


def list_test_faces_info(test_faces_dir: Optional[str] = None) -> List[dict]:
	"""
	List test faces with additional information.
	
	Args:
		test_faces_dir: Optional directory containing test faces
	
	Returns:
		List of dictionaries with test face information
	"""
	test_faces = get_test_faces(test_faces_dir)
	result = []
	
	for face_path in test_faces:
		path = Path(face_path)
		result.append({
			'path': face_path,
			'name': path.name,
			'size': path.stat().st_size if path.exists() else 0
		})
	
	return result
