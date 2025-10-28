"""Repository storage module for managing face data."""

import json
import os
import pickle
from typing import Dict, List, Optional

import numpy

from facefusion.face_analyser import get_many_faces
from facefusion.filesystem import create_directory, is_directory, is_file
from facefusion.types import Face
from facefusion.vision import read_static_image


def get_repository_path() -> str:
	"""Get the path to the repository directory."""
	return os.path.join(os.path.expanduser('~'), '.facefusion_repository')


def init_repository() -> bool:
	"""Initialize the repository structure."""
	repository_path = get_repository_path()
	
	if not is_directory(repository_path):
		create_directory(repository_path)
	
	persons_path = os.path.join(repository_path, 'persons')
	if not is_directory(persons_path):
		create_directory(persons_path)
	
	return is_directory(repository_path) and is_directory(persons_path)


def get_person_directory(person_name: str) -> str:
	"""Get the directory path for a specific person."""
	return os.path.join(get_repository_path(), 'persons', person_name)


def person_exists(person_name: str) -> bool:
	"""Check if a person exists in the repository."""
	return is_directory(get_person_directory(person_name))


def create_person(person_name: str) -> bool:
	"""Create a new person in the repository."""
	person_dir = get_person_directory(person_name)
	
	if not is_directory(person_dir):
		create_directory(person_dir)
	
	return is_directory(person_dir)


def add_face_to_person(person_name: str, image_path: str) -> Optional[Dict]:
	"""Add a face from an image to a person's repository.
	
	Args:
		person_name: Name of the person
		image_path: Path to the image containing the face
		
	Returns:
		Dictionary with face data if successful, None otherwise
	"""
	if not is_file(image_path):
		return None
	
	# Ensure person exists
	if not person_exists(person_name):
		if not create_person(person_name):
			return None
	
	# Extract face from image
	vision_frame = read_static_image(image_path)
	faces = get_many_faces([vision_frame])
	
	if not faces:
		return None
	
	# Use the first/largest face
	face = faces[0]
	
	# Generate unique face ID based on timestamp
	import time
	face_id = f"face_{int(time.time() * 1000)}"
	
	# Save face data
	person_dir = get_person_directory(person_name)
	face_file = os.path.join(person_dir, f"{face_id}.pkl")
	
	face_data = {
		'face_id': face_id,
		'source_image': image_path,
		'bounding_box': face.bounding_box.tolist(),
		'landmark_set': {k: v.tolist() for k, v in face.landmark_set.items()},
		'angle': face.angle,
		'embedding': face.embedding.tolist(),
		'embedding_norm': face.embedding_norm.tolist(),
		'gender': face.gender,
		'age': list(face.age),
		'race': face.race,
		'score_set': dict(face.score_set)
	}
	
	# Save to pickle file
	with open(face_file, 'wb') as f:
		pickle.dump(face_data, f)
	
	# Also save metadata as JSON for easy inspection
	metadata_file = os.path.join(person_dir, f"{face_id}.json")
	metadata = {
		'face_id': face_id,
		'source_image': image_path,
		'gender': face.gender,
		'age': list(face.age),
		'race': face.race
	}
	with open(metadata_file, 'w') as f:
		json.dump(metadata, f, indent=2)
	
	return face_data


def load_person_faces(person_name: str) -> List[Face]:
	"""Load all faces for a person from the repository.
	
	Args:
		person_name: Name of the person
		
	Returns:
		List of Face objects
	"""
	if not person_exists(person_name):
		return []
	
	person_dir = get_person_directory(person_name)
	face_files = [f for f in os.listdir(person_dir) if f.endswith('.pkl')]
	
	faces = []
	for face_file in face_files:
		face_path = os.path.join(person_dir, face_file)
		
		try:
			with open(face_path, 'rb') as f:
				face_data = pickle.load(f)
			
			# Reconstruct Face namedtuple
			face = Face(
				bounding_box=numpy.array(face_data['bounding_box']),
				score_set=face_data['score_set'],
				landmark_set={k: numpy.array(v) for k, v in face_data['landmark_set'].items()},
				angle=face_data['angle'],
				embedding=numpy.array(face_data['embedding']),
				embedding_norm=numpy.array(face_data['embedding_norm']),
				gender=face_data['gender'],
				age=range(face_data['age'][0], face_data['age'][-1] + 1),
				race=face_data['race']
			)
			faces.append(face)
		except Exception:
			# Skip corrupted files
			continue
	
	return faces


def list_persons() -> List[str]:
	"""List all persons in the repository.
	
	Returns:
		List of person names
	"""
	repository_path = get_repository_path()
	persons_path = os.path.join(repository_path, 'persons')
	
	if not is_directory(persons_path):
		return []
	
	persons = []
	for item in os.listdir(persons_path):
		item_path = os.path.join(persons_path, item)
		if is_directory(item_path):
			persons.append(item)
	
	return sorted(persons)


def count_person_faces(person_name: str) -> int:
	"""Count the number of faces for a person.
	
	Args:
		person_name: Name of the person
		
	Returns:
		Number of faces
	"""
	if not person_exists(person_name):
		return 0
	
	person_dir = get_person_directory(person_name)
	face_files = [f for f in os.listdir(person_dir) if f.endswith('.pkl')]
	
	return len(face_files)
