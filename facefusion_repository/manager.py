"""Manager for repository operations."""

import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from facefusion import logger
from facefusion_repository.orientation import check_orientation_overlap, extract_orientation_from_image_path
from facefusion_repository.quality_assessor import assess_face_from_path
from facefusion_repository.storage import Storage
from facefusion_repository.types import FaceMetadata, PersonEntry


class RepositoryManager:
	"""High-level manager for repository operations."""

	def __init__(self, repository_path: str = None):
		if repository_path is None:
			repository_path = '.face_repository'
		self.storage = Storage(repository_path)

	def create_person(
		self,
		display_name: str,
		face_paths: List[str],
		quality_threshold: Optional[float] = None,
		assess_quality: bool = True,
		extract_orientation: bool = True,
		orientation_tolerance: float = 15.0
	) -> PersonEntry:
		"""
		Create a new person in the repository.
		
		Args:
			display_name: Display name for the person
			face_paths: Paths to face images
			quality_threshold: Optional minimum quality threshold (0.0 to 1.0)
			assess_quality: Whether to assess face quality (default: True)
			extract_orientation: Whether to extract face orientation (default: True)
			orientation_tolerance: Tolerance for detecting orientation overlaps in degrees (default: 15.0)
		
		Returns:
			PersonEntry for the created person
		"""
		person_id = str(uuid.uuid4())
		
		# Copy face images to repository
		person_face_dir = self.storage.get_person_face_dir(person_id)
		stored_face_paths = []
		face_metadata: Dict[str, FaceMetadata] = {}
		existing_orientations = []
		
		for face_path in face_paths:
			if Path(face_path).exists():
				metadata: FaceMetadata = {}
				
				# Extract orientation first (before copying)
				orientation = None
				if extract_orientation:
					orientation = extract_orientation_from_image_path(face_path)
					if orientation:
						# Check for orientation overlap with existing faces
						overlap_idx = check_orientation_overlap(
							orientation,
							existing_orientations,
							orientation_tolerance
						)
						
						if overlap_idx is not None:
							# Orientation overlap detected
							logger.warn(
								f"Orientation overlap detected for {face_path} with existing face at index {overlap_idx}",
								__name__.upper()
							)
							
							# If assess_quality is enabled, compare quality
							if assess_quality:
								# Assess quality of new face
								new_quality = assess_face_from_path(face_path)
								
								# Get quality of existing face with overlapping orientation
								existing_face_path = stored_face_paths[overlap_idx]
								existing_metadata = face_metadata.get(existing_face_path, {})
								existing_quality_overall = existing_metadata.get('quality', {}).get('overall', 0.0)
								
								# Replace if new face has better quality
								if new_quality.overall > existing_quality_overall:
									logger.info(
										f"Replacing face at index {overlap_idx} with higher quality face (new: {new_quality.overall:.2f}, old: {existing_quality_overall:.2f})",
										__name__.upper()
									)
									# Remove old face file
									Path(existing_face_path).unlink(missing_ok=True)
									# Remove from lists
									stored_face_paths.pop(overlap_idx)
									face_metadata.pop(existing_face_path, None)
									existing_orientations.pop(overlap_idx)
								else:
									# Skip new face (existing is better quality)
									logger.info(
										f"Skipping face {face_path} (quality: {new_quality.overall:.2f}) - existing face has better quality: {existing_quality_overall:.2f}",
										__name__.upper()
									)
									continue
							else:
								# No quality assessment, skip the new face
								logger.info(
									f"Skipping face {face_path} due to orientation overlap (tolerance: {orientation_tolerance}°)",
									__name__.upper()
								)
								continue
				
				# Copy face to repository
				dest_path = person_face_dir / Path(face_path).name
				shutil.copy2(face_path, dest_path)
				dest_path_str = str(dest_path)
				
				# Store orientation if extracted
				if orientation:
					metadata['pose'] = orientation
					existing_orientations.append(orientation)
				
				# Assess quality if enabled
				if assess_quality:
					quality_metrics = assess_face_from_path(face_path)
					
					# Check quality threshold
					if quality_threshold is not None and quality_metrics.overall < quality_threshold:
						# Skip this face if below threshold
						Path(dest_path).unlink(missing_ok=True)  # Remove copied file
						if orientation:
							existing_orientations.pop()  # Remove from orientations
						continue
					
					# Store quality metrics
					metadata['quality'] = {
						'sharpness': quality_metrics.sharpness,
						'brightness': quality_metrics.brightness,
						'contrast': quality_metrics.contrast,
						'resolution': quality_metrics.resolution,
						'overall': quality_metrics.overall
					}
				
				# Store metadata if any
				if metadata:
					face_metadata[dest_path_str] = metadata
				
				stored_face_paths.append(dest_path_str)
		
		person: PersonEntry = {
			'person_id': person_id,
			'display_name': display_name,
			'face_paths': stored_face_paths,
			'face_count': len(stored_face_paths),
			'metadata': {},
			'face_metadata': face_metadata if face_metadata else None
		}
		
		self.storage.add_person(person)
		return person

	def get_person(self, person_id: str) -> Optional[PersonEntry]:
		"""Get a person by ID."""
		return self.storage.get_person(person_id)

	def get_person_by_name(self, display_name: str) -> Optional[PersonEntry]:
		"""Get a person by display name."""
		persons = self.storage.get_all_persons()
		for person in persons.values():
			if person['display_name'] == display_name:
				return person
		return None

	def list_persons(self) -> List[PersonEntry]:
		"""List all persons in the repository."""
		persons = self.storage.get_all_persons()
		return list(persons.values())

	def remove_person(self, person_id: str) -> bool:
		"""Remove a person from the repository."""
		person = self.storage.get_person(person_id)
		if person:
			# Remove face files
			person_face_dir = self.storage.get_person_face_dir(person_id)
			if person_face_dir.exists():
				shutil.rmtree(person_face_dir)
			
			# Remove from storage
			return self.storage.remove_person(person_id)
		return False

	def add_faces_to_person(
		self,
		person_id: str,
		face_paths: List[str],
		quality_threshold: Optional[float] = None,
		assess_quality: bool = True,
		extract_orientation: bool = True,
		orientation_tolerance: float = 15.0
	) -> bool:
		"""
		Add more faces to an existing person.
		
		Args:
			person_id: ID of the person
			face_paths: Paths to face images to add
			quality_threshold: Optional minimum quality threshold (0.0 to 1.0)
			assess_quality: Whether to assess face quality (default: True)
			extract_orientation: Whether to extract face orientation (default: True)
			orientation_tolerance: Tolerance for detecting orientation overlaps in degrees (default: 15.0)
		
		Returns:
			True if successful, False otherwise
		"""
		person = self.storage.get_person(person_id)
		if not person:
			return False
		
		person_face_dir = self.storage.get_person_face_dir(person_id)
		stored_face_paths = list(person['face_paths'])
		face_metadata = dict(person.get('face_metadata') or {})
		
		# Collect existing orientations
		existing_orientations = []
		if extract_orientation:
			for existing_path in stored_face_paths:
				existing_meta = face_metadata.get(existing_path, {})
				if 'pose' in existing_meta:
					existing_orientations.append(existing_meta['pose'])
		
		for face_path in face_paths:
			if Path(face_path).exists():
				metadata: FaceMetadata = {}
				
				# Extract orientation first (before copying)
				orientation = None
				if extract_orientation:
					orientation = extract_orientation_from_image_path(face_path)
					if orientation:
						# Check for orientation overlap with existing faces
						overlap_idx = check_orientation_overlap(
							orientation,
							existing_orientations,
							orientation_tolerance
						)
						
						if overlap_idx is not None:
							# Orientation overlap detected
							logger.warn(
								f"Orientation overlap detected for {face_path} with existing face at index {overlap_idx}",
								__name__.upper()
							)
							
							# If assess_quality is enabled, compare quality
							if assess_quality:
								# Assess quality of new face
								new_quality = assess_face_from_path(face_path)
								
								# Get quality of existing face with overlapping orientation
								existing_face_path = stored_face_paths[overlap_idx]
								existing_metadata = face_metadata.get(existing_face_path, {})
								existing_quality_overall = existing_metadata.get('quality', {}).get('overall', 0.0)
								
								# Replace if new face has better quality
								if new_quality.overall > existing_quality_overall:
									logger.info(
										f"Replacing face at index {overlap_idx} with higher quality face (new: {new_quality.overall:.2f}, old: {existing_quality_overall:.2f})",
										__name__.upper()
									)
									# Remove old face file
									Path(existing_face_path).unlink(missing_ok=True)
									# Remove from lists
									stored_face_paths.pop(overlap_idx)
									face_metadata.pop(existing_face_path, None)
									existing_orientations.pop(overlap_idx)
								else:
									# Skip new face (existing is better quality)
									logger.info(
										f"Skipping face {face_path} (quality: {new_quality.overall:.2f}) - existing face has better quality: {existing_quality_overall:.2f}",
										__name__.upper()
									)
									continue
							else:
								# No quality assessment, skip the new face
								logger.info(
									f"Skipping face {face_path} due to orientation overlap (tolerance: {orientation_tolerance}°)",
									__name__.upper()
								)
								continue
				
				# Copy face to repository
				dest_path = person_face_dir / Path(face_path).name
				shutil.copy2(face_path, dest_path)
				dest_path_str = str(dest_path)
				
				# Store orientation if extracted
				if orientation:
					metadata['pose'] = orientation
					existing_orientations.append(orientation)
				
				# Assess quality if enabled
				if assess_quality:
					quality_metrics = assess_face_from_path(face_path)
					
					# Check quality threshold
					if quality_threshold is not None and quality_metrics.overall < quality_threshold:
						# Skip this face if below threshold
						Path(dest_path).unlink(missing_ok=True)  # Remove copied file
						if orientation:
							existing_orientations.pop()  # Remove from orientations
						continue
					
					# Store quality metrics
					metadata['quality'] = {
						'sharpness': quality_metrics.sharpness,
						'brightness': quality_metrics.brightness,
						'contrast': quality_metrics.contrast,
						'resolution': quality_metrics.resolution,
						'overall': quality_metrics.overall
					}
				
				# Store metadata if any
				if metadata:
					face_metadata[dest_path_str] = metadata
				
				stored_face_paths.append(dest_path_str)
		
		return self.storage.update_person(person_id, {
			'face_paths': stored_face_paths,
			'face_count': len(stored_face_paths),
			'face_metadata': face_metadata if face_metadata else None
		})
