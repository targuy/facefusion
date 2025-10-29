"""Zone management for 3D face coverage."""

import math
from typing import Dict, List, Optional, Tuple

from facefusion_repository.types import CoverageZone, FaceMetadata, PoseMetricsDict


def calculate_zone_from_orientation(
	orientation: PoseMetricsDict,
	tolerance: float = 15.0
) -> CoverageZone:
	"""
	Calculate coverage zone from face orientation.
	
	Args:
		orientation: Face orientation (pitch, yaw, roll)
		tolerance: Angle tolerance for zone boundaries in degrees
	
	Returns:
		CoverageZone with angle ranges
	"""
	pitch = orientation.get('pitch', 0.0)
	yaw = orientation.get('yaw', 0.0)
	roll = orientation.get('roll', 0.0)
	
	# Calculate ranges with tolerance
	zone: CoverageZone = {
		'pitch_range': (pitch - tolerance, pitch + tolerance),
		'yaw_range': (yaw - tolerance, yaw + tolerance),
		'roll_range': (roll - tolerance, roll + tolerance)
	}
	
	return zone


def check_zone_overlap(
	zone1: CoverageZone,
	zone2: CoverageZone
) -> bool:
	"""
	Check if two coverage zones overlap.
	
	Args:
		zone1: First coverage zone
		zone2: Second coverage zone
	
	Returns:
		True if zones overlap, False otherwise
	"""
	# Check pitch overlap
	pitch1_min, pitch1_max = zone1.get('pitch_range', (-90.0, 90.0))
	pitch2_min, pitch2_max = zone2.get('pitch_range', (-90.0, 90.0))
	pitch_overlap = not (pitch1_max < pitch2_min or pitch2_max < pitch1_min)
	
	# Check yaw overlap (handle circular wrapping)
	yaw1_min, yaw1_max = zone1.get('yaw_range', (-180.0, 180.0))
	yaw2_min, yaw2_max = zone2.get('yaw_range', (-180.0, 180.0))
	
	# Simple overlap check (can be enhanced for circular wrapping)
	yaw_overlap = not (yaw1_max < yaw2_min or yaw2_max < yaw1_min)
	
	# Check roll overlap
	roll1_min, roll1_max = zone1.get('roll_range', (-180.0, 180.0))
	roll2_min, roll2_max = zone2.get('roll_range', (-180.0, 180.0))
	roll_overlap = not (roll1_max < roll2_min or roll2_max < roll1_min)
	
	# All three axes must overlap for zone overlap
	return pitch_overlap and yaw_overlap and roll_overlap


def calculate_optimal_coverage_zones(
	new_face_orientation: PoseMetricsDict,
	existing_zones: List[CoverageZone],
	new_face_quality: float,
	tolerance: float = 15.0
) -> Tuple[CoverageZone, List[CoverageZone]]:
	"""
	Calculate optimal coverage zones for new face.
	
	Determines the zone for a new face and adjusts existing zones if overlap occurs.
	
	Args:
		new_face_orientation: Orientation of new face
		existing_zones: List of existing coverage zones
		new_face_quality: Quality score of new face
		tolerance: Zone tolerance in degrees
	
	Returns:
		Tuple of (new_zone, updated_existing_zones)
	"""
	# Calculate new zone
	new_zone = calculate_zone_from_orientation(new_face_orientation, tolerance)
	
	# Check for overlaps with existing zones
	overlapping_indices = []
	for idx, existing_zone in enumerate(existing_zones):
		if check_zone_overlap(new_zone, existing_zone):
			overlapping_indices.append(idx)
	
	if not overlapping_indices:
		# No overlap, return new zone as-is
		return new_zone, existing_zones
	
	# For minimal changes, keep zones as-is
	# In a full implementation, this would split/adjust zones based on quality
	return new_zone, existing_zones


def resolve_zone_conflict(
	existing_face_metadata: FaceMetadata,
	new_face_metadata: FaceMetadata,
	user_choice: Dict[str, str],
	tolerance: float = 15.0
) -> Tuple[List[CoverageZone], List[CoverageZone]]:
	"""
	Resolve zone conflict based on user preference.
	
	Args:
		existing_face_metadata: Metadata of existing face
		new_face_metadata: Metadata of new face
		user_choice: User's zone preference (zone_id -> 'existing' or 'new')
		tolerance: Zone tolerance in degrees
	
	Returns:
		Tuple of (existing_zones, new_zones)
	"""
	existing_orientation = existing_face_metadata.get('pose', {})
	new_orientation = new_face_metadata.get('pose', {})
	
	# Get or create zones
	existing_zones = existing_face_metadata.get('coverage_zones', [])
	if not existing_zones:
		existing_zones = [calculate_zone_from_orientation(existing_orientation, tolerance)]
	
	new_zones = new_face_metadata.get('coverage_zones', [])
	if not new_zones:
		new_zones = [calculate_zone_from_orientation(new_orientation, tolerance)]
	
	# Apply user choices
	# For minimal implementation, keep both zones separate
	# In full implementation, this would split zones based on user_choice
	
	return existing_zones, new_zones


def get_zone_center(zone: CoverageZone) -> PoseMetricsDict:
	"""
	Get center orientation of a coverage zone.
	
	Args:
		zone: Coverage zone
	
	Returns:
		Center orientation as PoseMetricsDict
	"""
	pitch_min, pitch_max = zone.get('pitch_range', (0.0, 0.0))
	yaw_min, yaw_max = zone.get('yaw_range', (0.0, 0.0))
	roll_min, roll_max = zone.get('roll_range', (0.0, 0.0))
	
	return {
		'pitch': (pitch_min + pitch_max) / 2,
		'yaw': (yaw_min + yaw_max) / 2,
		'roll': (roll_min + roll_max) / 2
	}


def format_zone_description(zone: CoverageZone) -> str:
	"""
	Format zone description for display.
	
	Args:
		zone: Coverage zone
	
	Returns:
		Human-readable zone description
	"""
	pitch_min, pitch_max = zone.get('pitch_range', (0.0, 0.0))
	yaw_min, yaw_max = zone.get('yaw_range', (0.0, 0.0))
	roll_min, roll_max = zone.get('roll_range', (0.0, 0.0))
	
	return f"Pitch: [{pitch_min:.1f}°, {pitch_max:.1f}°], Yaw: [{yaw_min:.1f}°, {yaw_max:.1f}°], Roll: [{roll_min:.1f}°, {roll_max:.1f}°]"
