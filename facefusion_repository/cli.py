"""
CLI commands for repository management.
"""

from typing import Optional

from facefusion import face_analyser, logger, wording
from facefusion.filesystem import is_image
from facefusion.types import ErrorCode
from facefusion.vision import read_static_image
from facefusion_repository.manager import RepositoryManager


def repo_init(repository_path: str = '.facefusion_repository') -> ErrorCode:
	"""Initialize a new face repository.
	
	Args:
		repository_path: Path to the repository directory
		
	Returns:
		Error code (0 for success, non-zero for failure)
	"""
	manager = RepositoryManager(repository_path)
	
	if manager.exists():
		logger.error('Repository already exists at: ' + repository_path, __name__)
		return 1
	
	if manager.initialize():
		logger.info('Repository initialized successfully at: ' + repository_path, __name__)
		return 0
	else:
		logger.error('Failed to initialize repository at: ' + repository_path, __name__)
		return 1


def repo_add(person_name: str, source_path: str, repository_path: str = '.facefusion_repository') -> ErrorCode:
	"""Add a face to the repository.
	
	Args:
		person_name: Name of the person
		source_path: Path to the face image
		repository_path: Path to the repository directory
		
	Returns:
		Error code (0 for success, non-zero for failure)
	"""
	manager = RepositoryManager(repository_path)
	
	if not manager.exists():
		logger.error('Repository does not exist. Initialize it first with repo-init.', __name__)
		return 1
	
	if not is_image(source_path):
		logger.error('Source file is not a valid image: ' + source_path, __name__)
		return 1
	
	# Read image and detect face
	try:
		vision_frame = read_static_image(source_path)
		if vision_frame is None:
			logger.error('Failed to read image: ' + source_path, __name__)
			return 1
		
		# Detect face
		face = face_analyser.get_one_face(vision_frame)
		if face is None:
			logger.error('No face detected in image: ' + source_path, __name__)
			return 1
		
		# Extract embedding
		embedding = face.embedding.tolist() if face.embedding is not None else []
		
		# Calculate quality score (using detector score)
		quality_score = face.score_set.get('detector', 0.0) if face.score_set else 0.0
		
		# Add to repository
		if manager.add_face(person_name, source_path, embedding, quality_score):
			logger.info(f'Added face for "{person_name}" from: {source_path}', __name__)
			logger.info(f'Quality score: {quality_score:.2f}', __name__)
			return 0
		else:
			logger.error('Failed to add face to repository', __name__)
			return 1
			
	except Exception as e:
		logger.error(f'Error adding face: {str(e)}', __name__)
		return 1


def repo_list(repository_path: str = '.facefusion_repository') -> ErrorCode:
	"""List all persons and their faces in the repository.
	
	Args:
		repository_path: Path to the repository directory
		
	Returns:
		Error code (0 for success, non-zero for failure)
	"""
	manager = RepositoryManager(repository_path)
	
	if not manager.exists():
		logger.error('Repository does not exist. Initialize it first with repo-init.', __name__)
		return 1
	
	persons = manager.list_persons()
	
	if not persons:
		logger.info('Repository is empty. Add faces with repo-add.', __name__)
		return 0
	
	logger.info(f'\nRepository contains {len(persons)} person(s):\n', __name__)
	
	for person_name in persons:
		person = manager.get_person(person_name)
		if person:
			face_count = len(person['faces'])
			logger.info(f'  • {person_name}: {face_count} face(s)', __name__)
			
			for idx, face in enumerate(person['faces'], 1):
				quality = face.get('quality_score', 0.0)
				logger.info(f'    [{idx}] Quality: {quality:.2f} - {face["path"]}', __name__)
	
	return 0


def repo_execute(person_name: str, target_path: str, output_path: str, repository_path: str = '.facefusion_repository') -> ErrorCode:
	"""Execute face swapping using repository faces.
	
	Args:
		person_name: Name of the person whose faces to use
		target_path: Path to the target image/video
		output_path: Path for the output
		repository_path: Path to the repository directory
		
	Returns:
		Error code (0 for success, non-zero for failure)
	"""
	from facefusion import state_manager
	
	manager = RepositoryManager(repository_path)
	
	if not manager.exists():
		logger.error('Repository does not exist. Initialize it first with repo-init.', __name__)
		return 1
	
	person = manager.get_person(person_name)
	if person is None:
		logger.error(f'Person "{person_name}" not found in repository', __name__)
		return 1
	
	if not person['faces']:
		logger.error(f'Person "{person_name}" has no faces in repository', __name__)
		return 1
	
	# Get face paths from repository
	face_paths = manager.get_person_face_paths(person_name)
	
	if not face_paths:
		logger.error(f'No valid face images found for person "{person_name}"', __name__)
		return 1
	
	logger.info(f'Using {len(face_paths)} face(s) from "{person_name}" for face swapping', __name__)
	
	# Set up state for processing
	state_manager.set_item('source_paths', face_paths)
	state_manager.set_item('target_path', target_path)
	state_manager.set_item('output_path', output_path)
	
	# Import and run the conditional_process from core
	from facefusion.core import conditional_process
	
	try:
		error_code = conditional_process()
		
		if error_code == 0:
			logger.info(f'Face swapping completed successfully. Output saved to: {output_path}', __name__)
		else:
			logger.error(f'Face swapping failed with error code: {error_code}', __name__)
		
		return error_code
		
	except Exception as e:
		logger.error(f'Error during face swapping: {str(e)}', __name__)
		return 1
