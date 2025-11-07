"""Helper functions for repository integration."""

from typing import List, Optional

from facefusion import logger, state_manager


def get_effective_source_paths() -> List[str]:
	"""
	Get effective source face paths based on priority.
	
	Priority (IMPORTANT):
	1. Direct upload (source_paths) - ALWAYS HAS PRIORITY if present
	2. Repository (repository_source_faces) - Used only if no direct upload
	
	This ensures that when user uploads an image directly, it overrides
	any repository selection, providing intuitive behavior.
	
	Returns:
		List of face paths (empty list if no sources available)
	"""
	# PRIORITY 1: Check direct upload first (source_paths)
	source_paths = state_manager.get_item('source_paths')
	if source_paths:
		logger.debug(f"Using direct upload mode: {len(source_paths)} faces (PRIORITY)", __name__.upper())
		return source_paths
	
	# PRIORITY 2: Fallback to repository if no direct upload
	repository_mode = state_manager.get_item('repository_mode')
	if repository_mode:
		repo_faces = state_manager.get_item('repository_source_faces')
		if repo_faces:
			person_name = state_manager.get_item('repository_person_name')
			logger.debug(f"Using repository mode: {len(repo_faces)} faces from '{person_name}'", __name__.upper())
			return repo_faces
	
	# No sources available
	return []


def is_repository_mode_active() -> bool:
	"""
	Check if repository mode is currently active.
	
	Returns:
		True if repository mode is active, False otherwise
	"""
	return bool(state_manager.get_item('repository_mode'))


def get_repository_person_name() -> Optional[str]:
	"""
	Get the currently selected repository person name.
	
	Returns:
		Person name or None if no person selected
	"""
	if is_repository_mode_active():
		return state_manager.get_item('repository_person_name')
	return None


def get_repository_person_id() -> Optional[str]:
	"""
	Get the currently selected repository person ID.
	
	Returns:
		Person ID or None if no person selected
	"""
	if is_repository_mode_active():
		return state_manager.get_item('repository_person_id')
	return None
