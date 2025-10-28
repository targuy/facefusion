"""Video executor for repository-based face swapping."""

from typing import List, Optional

from facefusion import logger, state_manager
from facefusion.face_analyser import get_many_faces, scale_face
from facefusion.processors.modules.face_swapper import swap_face
from facefusion.types import Face, VisionFrame
from facefusion_repository import storage
from facefusion_repository.selector import select_optimal_face


# Cache for repository faces to avoid reloading
_repository_cache = {}


def get_repository_faces(person_name: str) -> List[Face]:
	"""Get repository faces for a person with caching.
	
	Args:
		person_name: Name of the person
		
	Returns:
		List of Face objects from repository
	"""
	if person_name not in _repository_cache:
		_repository_cache[person_name] = storage.load_person_faces(person_name)
	
	return _repository_cache[person_name]


def clear_repository_cache() -> None:
	"""Clear the repository faces cache."""
	global _repository_cache
	_repository_cache = {}


def extract_optimal_source_face(person_name: str, target_face: Face) -> Optional[Face]:
	"""Extract optimal source face from repository based on target face orientation.
	
	Args:
		person_name: Name of the person in repository
		target_face: Target face to match
		
	Returns:
		Optimal Face from repository or None
	"""
	repository_faces = get_repository_faces(person_name)
	
	if not repository_faces:
		logger.warn(f"No faces found in repository for person '{person_name}'", __name__)
		return None
	
	# Select optimal face based on pose similarity
	optimal_face = select_optimal_face(target_face, repository_faces)
	
	return optimal_face


def process_frame_with_repository(person_name: str,
                                  reference_vision_frame: VisionFrame,
                                  target_vision_frame: VisionFrame,
                                  temp_vision_frame: VisionFrame) -> VisionFrame:
	"""Process a frame using repository-based face selection.
	
	Args:
		person_name: Name of the person in repository
		reference_vision_frame: Reference frame for face selection
		target_vision_frame: Target frame with faces to swap
		temp_vision_frame: Temporary frame to modify
		
	Returns:
		Processed frame with swapped faces
	"""
	from facefusion.face_selector import select_faces
	
	# Get target faces from frame
	target_faces = select_faces(reference_vision_frame, target_vision_frame)
	
	if not target_faces:
		return temp_vision_frame
	
	# Process each target face
	for target_face in target_faces:
		# Get optimal source face from repository
		source_face = extract_optimal_source_face(person_name, target_face)
		
		if source_face:
			# Scale target face to match temp frame if needed
			target_face = scale_face(target_face, target_vision_frame, temp_vision_frame)
			
			# Swap face using existing face_swapper logic
			temp_vision_frame = swap_face(source_face, target_face, temp_vision_frame)
	
	return temp_vision_frame
