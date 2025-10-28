"""Repository manager for high-level repository operations."""

from typing import List, Optional

from facefusion import logger, wording
from facefusion_repository import storage


def init_repository() -> bool:
	"""Initialize the repository structure.
	
	Returns:
		True if successful, False otherwise
	"""
	if storage.init_repository():
		logger.info('Repository initialized successfully', __name__)
		return True
	else:
		logger.error('Failed to initialize repository', __name__)
		return False


def add_person_face(person_name: str, image_path: str) -> bool:
	"""Add a face image to a person's repository.
	
	Args:
		person_name: Name of the person
		image_path: Path to the image containing the face
		
	Returns:
		True if successful, False otherwise
	"""
	face_data = storage.add_face_to_person(person_name, image_path)
	
	if face_data:
		logger.info(f"Added face to repository for person '{person_name}' from {image_path}", __name__)
		return True
	else:
		logger.error(f"Failed to add face for person '{person_name}' from {image_path}", __name__)
		return False


def list_repository_persons() -> List[str]:
	"""List all persons in the repository.
	
	Returns:
		List of person names
	"""
	return storage.list_persons()


def get_person_info(person_name: str) -> Optional[dict]:
	"""Get information about a person in the repository.
	
	Args:
		person_name: Name of the person
		
	Returns:
		Dictionary with person info or None if not found
	"""
	if not storage.person_exists(person_name):
		return None
	
	face_count = storage.count_person_faces(person_name)
	
	return {
		'name': person_name,
		'face_count': face_count
	}
