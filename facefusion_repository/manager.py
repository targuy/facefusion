"""Manager for repository operations."""

import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from facefusion import logger
from facefusion_repository.orientation import check_orientation_overlap, extract_orientation_from_image_path
from facefusion_repository.quality_assessor import assess_face_from_path
from facefusion_repository.storage import Storage
from facefusion_repository.types import FaceMetadata, PersonEntry
from facefusion_repository.zone_manager import calculate_zone_from_orientation


class RepositoryManager:
	"""High-level manager for repository operations."""

	def __init__(self, repository_path: str = None):
		if repository_path is None:
			repository_path = '.face_repository'
		self.storage = Storage(repository_path)

	@staticmethod
	def _normalize_name(name: str) -> str:
		"""
		Normalize a person name for uniqueness checking.
		
		Args:
			name: Display name to normalize
		
		Returns:
			Normalized name (lowercase, stripped)
		"""
		return name.strip().lower()

	def get_person_by_normalized_name(self, display_name: str) -> Optional[PersonEntry]:
		"""
		Get a person by normalized display name (case-insensitive).
		
		Args:
			display_name: Display name to search for
		
		Returns:
			PersonEntry if found, None otherwise
		"""
		normalized = self._normalize_name(display_name)
		persons = self.storage.get_all_persons()
		for person in persons.values():
			if person.get('normalized_name', self._normalize_name(person['display_name'])) == normalized:
				return person
		return None

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
		
		Raises:
			ValueError: If a person with the same name (case-insensitive) already exists
		"""
		# Check for duplicate name
		normalized_name = self._normalize_name(display_name)
		existing_person = self.get_person_by_normalized_name(display_name)
		if existing_person:
			raise ValueError(
				f"Person with name '{display_name}' already exists (ID: {existing_person['person_id']}). "
				f"Use add_faces_to_person() to add more faces or choose a different name."
			)
		
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
			'normalized_name': normalized_name,
			'face_paths': stored_face_paths,
			'face_count': len(stored_face_paths),
			'metadata': {},
			'face_metadata': face_metadata if face_metadata else None
		}
		
		self.storage.add_person(person)
		return person

	def create_or_update_person(
		self,
		display_name: str,
		face_paths: List[str],
		quality_threshold: Optional[float] = None,
		assess_quality: bool = True,
		extract_orientation: bool = True,
		orientation_tolerance: float = 15.0
	) -> PersonEntry:
		"""
		Create a new person or add faces to existing person.
		
		This is the recommended method for adding faces to the repository.
		It automatically detects if a person with the given name exists
		and either creates a new entry or adds faces to the existing one.
		
		Args:
			display_name: Display name for the person
			face_paths: Paths to face images
			quality_threshold: Optional minimum quality threshold (0.0 to 1.0)
			assess_quality: Whether to assess face quality (default: True)
			extract_orientation: Whether to extract face orientation (default: True)
			orientation_tolerance: Tolerance for detecting orientation overlaps in degrees (default: 15.0)
		
		Returns:
			PersonEntry for the created or updated person
		"""
		# Check if person already exists (case-insensitive)
		existing_person = self.get_person_by_normalized_name(display_name)
		
		if existing_person:
			# Person exists → add faces
			logger.info(
				f"Person '{display_name}' already exists (ID: {existing_person['person_id']}), adding faces...",
				__name__.upper()
			)
			success = self.add_faces_to_person(
				existing_person['person_id'],
				face_paths,
				quality_threshold=quality_threshold,
				assess_quality=assess_quality,
				extract_orientation=extract_orientation,
				orientation_tolerance=orientation_tolerance
			)
			if success:
				# Return updated person
				return self.get_person(existing_person['person_id'])
			else:
				raise RuntimeError(f"Failed to add faces to person '{display_name}'")
		else:
			# Person doesn't exist → create new
			logger.info(
				f"Creating new person '{display_name}'...",
				__name__.upper()
			)
			return self.create_person(
				display_name,
				face_paths,
				quality_threshold=quality_threshold,
				assess_quality=assess_quality,
				extract_orientation=extract_orientation,
				orientation_tolerance=orientation_tolerance
			)

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

	def remove_face_from_person(self, person_id: str, face_path: str) -> bool:
		"""
		Remove a specific face from a person's repository.
		
		Args:
			person_id: ID of the person
			face_path: Path to the face image to remove
		
		Returns:
			True if face was removed successfully, False otherwise
		"""
		person = self.storage.get_person(person_id)
		if not person:
			return False
		
		# Remove face from person's face_paths list
		if face_path in person['face_paths']:
			person['face_paths'].remove(face_path)
			person['face_count'] = len(person['face_paths'])
			
			# Update storage
			self.storage.update_person(person_id, person)
			
			# Remove physical file
			import os
			if os.path.exists(face_path):
				os.remove(face_path)
			
			# Remove face metadata if present
			if 'face_metadata' in person and face_path in person['face_metadata']:
				del person['face_metadata'][face_path]
				self.storage.update_person(person_id, person)
			
			logger.info(
				f"Removed face from person '{person['display_name']}': {face_path}",
				__name__.upper()
			)
			return True
		
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
	
	def preview_face_import(
		self,
		face_path: str,
		test_faces_dir: Optional[str] = None,
		max_test_faces: int = 5
	) -> Dict[str, any]:
		"""
		Generate preview of face import on test faces.
		
		Args:
			face_path: Path to face to preview
			test_faces_dir: Optional directory with test faces
			max_test_faces: Maximum number of test faces to use
		
		Returns:
			Dictionary with preview results
		"""
		from facefusion_repository.preview import generate_import_preview
		from facefusion_repository.test_faces import get_test_faces
		
		# Get test faces
		test_faces = get_test_faces(test_faces_dir, max_test_faces)
		
		if not test_faces:
			logger.warn("No test faces found for preview", __name__.upper())
			return {'success': False, 'message': 'No test faces available'}
		
		# Generate previews
		preview_results = generate_import_preview(face_path, test_faces)
		
		return {
			'success': True,
			'test_face_count': len(test_faces),
			'preview_results': preview_results
		}
	
	def calculate_coverage_stats(self, person_id: str) -> Dict[str, Any]:
		"""
		Calculate coverage statistics for a person's faces.
		
		Analyzes the 3D orientation coverage of all faces in the repository
		to determine how well different angles are represented.
		
		Args:
			person_id: ID of the person
		
		Returns:
			Dictionary with coverage statistics:
			- total_faces: Total number of faces
			- unique_zones: Number of unique coverage zones
			- coverage_percentage: Estimated coverage percentage (0-100)
			- zone_distribution: Distribution of faces across zones
			- missing_zones: List of underrepresented zones
		"""
		person = self.storage.get_person(person_id)
		if not person:
			return {
				'success': False,
				'message': f'Person not found: {person_id}'
			}
		
		total_faces = person['face_count']
		if total_faces == 0:
			return {
				'success': True,
				'total_faces': 0,
				'unique_zones': 0,
				'coverage_percentage': 0.0,
				'zone_distribution': {},
				'missing_zones': []
			}
		
		# Extract orientations from face metadata
		face_metadata = person.get('face_metadata', {})
		orientations = []
		
		for face_path, metadata in face_metadata.items():
			pose = metadata.get('pose')
			if pose:
				orientations.append(pose)
		
		if not orientations:
			# No orientation data available
			return {
				'success': True,
				'total_faces': total_faces,
				'unique_zones': 0,
				'coverage_percentage': 0.0,
				'zone_distribution': {},
				'missing_zones': [],
				'warning': 'No orientation data available'
			}
		
		# Calculate zones from orientations
		zones = []
		zone_tolerance = 15.0  # degrees
		
		for orientation in orientations:
			zone = calculate_zone_from_orientation(orientation, zone_tolerance)
			zones.append(zone)
		
		# Group zones by approximate center (quantized to 30° grid)
		zone_grid = {}
		grid_size = 30.0  # degrees
		
		for zone in zones:
			# Get zone center
			pitch_range = zone.get('pitch_range', (0.0, 0.0))
			yaw_range = zone.get('yaw_range', (0.0, 0.0))
			
			pitch_center = (pitch_range[0] + pitch_range[1]) / 2
			yaw_center = (yaw_range[0] + yaw_range[1]) / 2
			
			# Quantize to grid
			pitch_bin = int(pitch_center / grid_size) * grid_size
			yaw_bin = int(yaw_center / grid_size) * grid_size
			
			grid_key = (pitch_bin, yaw_bin)
			zone_grid[grid_key] = zone_grid.get(grid_key, 0) + 1
		
		unique_zones = len(zone_grid)
		
		# Calculate coverage percentage
		# Ideal coverage: 8 yaw angles × 4 pitch angles = 32 zones
		# Yaw: [-180, -120, -60, 0, 60, 120, 180] (7 bins, but -180=180 → 6)
		# Pitch: [-30, 0, 30, 60] (4 bins)
		ideal_zones = 24  # 6 yaw × 4 pitch
		coverage_percentage = min(100.0, (unique_zones / ideal_zones) * 100.0)
		
		# Find missing zones (underrepresented areas)
		missing_zones = []
		for pitch in [-30, 0, 30]:
			for yaw in [-120, -60, 0, 60, 120]:
				grid_key = (pitch, yaw)
				if grid_key not in zone_grid:
					missing_zones.append({
						'pitch': pitch,
						'yaw': yaw,
						'description': f"Pitch {pitch}°, Yaw {yaw}°"
					})
		
		return {
			'success': True,
			'total_faces': total_faces,
			'unique_zones': unique_zones,
			'coverage_percentage': round(coverage_percentage, 1),
			'zone_distribution': zone_grid,
			'missing_zones': missing_zones[:5],  # Top 5 missing zones
			'ideal_zones': ideal_zones
		}

	def compare_faces_on_test_cases(
		self,
		existing_face_path: str,
		new_face_path: str,
		test_faces_dir: Optional[str] = None,
		max_test_faces: int = 5
	) -> Dict[str, any]:
		"""
		Compare two faces on test cases for overlap resolution.
		
		Args:
			existing_face_path: Path to existing repository face
			new_face_path: Path to new face candidate
			test_faces_dir: Optional directory with test faces
			max_test_faces: Maximum number of test faces to use
		
		Returns:
			Dictionary with comparison results
		"""
		from facefusion_repository.preview import compare_overlap_previews
		from facefusion_repository.test_faces import get_test_faces
		
		# Get test faces
		test_faces = get_test_faces(test_faces_dir, max_test_faces)
		
		if not test_faces:
			logger.warn("No test faces found for comparison", __name__.upper())
			return {'success': False, 'message': 'No test faces available'}
		
		# Generate comparisons
		comparison_results = compare_overlap_previews(
			existing_face_path,
			new_face_path,
			test_faces
		)
		
		return {
			'success': True,
			'test_face_count': len(test_faces),
			'comparison_results': comparison_results
		}
