"""Face selector for repository-based face selection."""

from typing import Dict, List, Optional, Tuple

from facefusion_repository.manager import RepositoryManager


class RepositorySelector:
	"""Selects faces from repository for processing."""

	def __init__(self, repository_manager: RepositoryManager):
		self.manager = repository_manager

	def get_person_faces(self, person_name: str) -> List[str]:
		"""Get all face paths for a person by name."""
		person = self.manager.get_person_by_name(person_name)
		if person:
			return person['face_paths']
		return []

	def get_best_person_face(
		self,
		person_name: str,
		quality_threshold: Optional[float] = None
	) -> Optional[str]:
		"""
		Get the best face for a person based on quality.
		
		Args:
			person_name: Person name
			quality_threshold: Optional minimum quality threshold
		
		Returns:
			Path to the best quality face, or None if no faces found
		"""
		person = self.manager.get_person_by_name(person_name)
		if not person:
			return None
		
		face_paths = person['face_paths']
		if not face_paths:
			return None
		
		# If no quality metadata, return first face
		face_metadata = person.get('face_metadata')
		if not face_metadata:
			return face_paths[0]
		
		# Filter by quality threshold if specified
		best_face = None
		best_quality = -1.0
		
		for face_path in face_paths:
			metadata = face_metadata.get(face_path)
			if metadata and 'quality' in metadata:
				quality = metadata['quality'].get('overall', 0.0)
				
				# Check quality threshold
				if quality_threshold is not None and quality < quality_threshold:
					continue
				
				# Track best quality face
				if quality > best_quality:
					best_quality = quality
					best_face = face_path
		
		# Return best face or fallback to first face
		return best_face if best_face else face_paths[0]

	def get_faces_by_quality(
		self,
		person_name: str,
		quality_threshold: float = 0.7,
		sort_by_quality: bool = True
	) -> List[str]:
		"""
		Get faces for a person filtered and optionally sorted by quality.
		
		Args:
			person_name: Person name
			quality_threshold: Minimum quality threshold (0.0 to 1.0)
			sort_by_quality: Whether to sort by quality (highest first)
		
		Returns:
			List of face paths meeting quality criteria
		"""
		person = self.manager.get_person_by_name(person_name)
		if not person:
			return []
		
		face_paths = person['face_paths']
		face_metadata = person.get('face_metadata')
		
		if not face_metadata:
			# No quality metadata, return all faces
			return face_paths
		
		# Filter and collect faces with quality scores
		faces_with_quality = []
		for face_path in face_paths:
			metadata = face_metadata.get(face_path)
			if metadata and 'quality' in metadata:
				quality = metadata['quality'].get('overall', 0.0)
				if quality >= quality_threshold:
					faces_with_quality.append((face_path, quality))
			else:
				# Include faces without quality metadata
				faces_with_quality.append((face_path, 0.0))
		
		# Sort by quality if requested
		if sort_by_quality:
			faces_with_quality.sort(key=lambda x: x[1], reverse=True)
		
		return [face_path for face_path, _ in faces_with_quality]

	def select_faces_for_person(
		self,
		person_name: str,
		fallback_persons: Optional[List[str]] = None,
		quality_threshold: Optional[float] = None,
		max_faces: Optional[int] = None
	) -> List[str]:
		"""
		Select faces for a person with optional fallback chain and quality filtering.
		
		Args:
			person_name: Primary person name
			fallback_persons: Optional list of fallback person names
			quality_threshold: Optional minimum quality threshold (0.0 to 1.0)
			max_faces: Optional maximum number of faces to return
		
		Returns:
			List of face paths to use as source faces
		"""
		# Try primary person
		if quality_threshold is not None:
			face_paths = self.get_faces_by_quality(person_name, quality_threshold)
		else:
			face_paths = self.get_person_faces(person_name)
		
		if face_paths:
			# Limit number of faces if specified
			if max_faces is not None:
				face_paths = face_paths[:max_faces]
			return face_paths
		
		# Try fallback persons
		if fallback_persons:
			for fallback_name in fallback_persons:
				if quality_threshold is not None:
					face_paths = self.get_faces_by_quality(fallback_name, quality_threshold)
				else:
					face_paths = self.get_person_faces(fallback_name)
				
				if face_paths:
					# Limit number of faces if specified
					if max_faces is not None:
						face_paths = face_paths[:max_faces]
					return face_paths
		
		return []

	def get_best_face_by_pose_similarity(
		self,
		person_name: str,
		target_pose: Tuple[float, float, float],
		orientation_tolerance: float = 15.0
	) -> Optional[str]:
		"""
		Get the best matching face based on pose similarity to target pose.
		
		Args:
			person_name: Person name
			target_pose: Target pose as (pitch, yaw, roll) in degrees
			orientation_tolerance: Maximum angular difference in degrees
		
		Returns:
			Path to best matching face, or None if no suitable face found
		"""
		from facefusion_repository.pose_calculator import calculate_pose_similarity, is_pose_within_tolerance
		
		person = self.manager.get_person_by_name(person_name)
		if not person:
			return None
		
		face_paths = person['face_paths']
		face_metadata = person.get('face_metadata')
		
		if not face_metadata:
			# No pose metadata, return first face
			return face_paths[0] if face_paths else None
		
		# Find best matching pose
		best_face = None
		best_similarity = -1.0
		
		for face_path in face_paths:
			metadata = face_metadata.get(face_path)
			if metadata and 'pose' in metadata:
				pose_data = metadata['pose']
				face_pose = (
					pose_data.get('pitch', 0.0),
					pose_data.get('yaw', 0.0),
					pose_data.get('roll', 0.0)
				)
				
				# Check if within tolerance
				if is_pose_within_tolerance(target_pose, face_pose, orientation_tolerance):
					similarity = calculate_pose_similarity(target_pose, face_pose)
					if similarity > best_similarity:
						best_similarity = similarity
						best_face = face_path
		
		# Return best matching face or fallback to first face
		return best_face if best_face else (face_paths[0] if face_paths else None)

