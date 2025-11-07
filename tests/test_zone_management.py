"""Unit tests for zone management functionality."""

import unittest
from facefusion_repository.zone_manager import (
	calculate_zone_from_orientation,
	check_zone_overlap,
	calculate_optimal_coverage_zones,
	get_zone_center,
	format_zone_description
)
from facefusion_repository.types import CoverageZone, PoseMetricsDict


class TestZoneManagement(unittest.TestCase):
	"""Test zone management functions."""
	
	def test_calculate_zone_from_orientation(self):
		"""Test zone calculation from orientation."""
		orientation: PoseMetricsDict = {
			'pitch': 10.0,
			'yaw': 20.0,
			'roll': 5.0
		}
		
		zone = calculate_zone_from_orientation(orientation, tolerance=15.0)
		
		# Check zone ranges
		self.assertEqual(zone['pitch_range'], (-5.0, 25.0))
		self.assertEqual(zone['yaw_range'], (5.0, 35.0))
		self.assertEqual(zone['roll_range'], (-10.0, 20.0))
	
	def test_calculate_zone_with_custom_tolerance(self):
		"""Test zone calculation with custom tolerance."""
		orientation: PoseMetricsDict = {
			'pitch': 0.0,
			'yaw': 0.0,
			'roll': 0.0
		}
		
		zone = calculate_zone_from_orientation(orientation, tolerance=10.0)
		
		self.assertEqual(zone['pitch_range'], (-10.0, 10.0))
		self.assertEqual(zone['yaw_range'], (-10.0, 10.0))
		self.assertEqual(zone['roll_range'], (-10.0, 10.0))
	
	def test_check_zone_overlap_overlapping(self):
		"""Test zone overlap detection with overlapping zones."""
		zone1: CoverageZone = {
			'pitch_range': (0.0, 20.0),
			'yaw_range': (0.0, 20.0),
			'roll_range': (0.0, 20.0)
		}
		
		zone2: CoverageZone = {
			'pitch_range': (10.0, 30.0),
			'yaw_range': (10.0, 30.0),
			'roll_range': (10.0, 30.0)
		}
		
		self.assertTrue(check_zone_overlap(zone1, zone2))
	
	def test_check_zone_overlap_non_overlapping(self):
		"""Test zone overlap detection with non-overlapping zones."""
		zone1: CoverageZone = {
			'pitch_range': (0.0, 10.0),
			'yaw_range': (0.0, 10.0),
			'roll_range': (0.0, 10.0)
		}
		
		zone2: CoverageZone = {
			'pitch_range': (30.0, 40.0),
			'yaw_range': (30.0, 40.0),
			'roll_range': (30.0, 40.0)
		}
		
		self.assertFalse(check_zone_overlap(zone1, zone2))
	
	def test_check_zone_overlap_partial(self):
		"""Test zone overlap with partial overlap on some axes."""
		zone1: CoverageZone = {
			'pitch_range': (0.0, 20.0),
			'yaw_range': (0.0, 20.0),
			'roll_range': (0.0, 20.0)
		}
		
		# Overlaps on pitch and yaw but not roll
		zone2: CoverageZone = {
			'pitch_range': (10.0, 30.0),
			'yaw_range': (10.0, 30.0),
			'roll_range': (40.0, 60.0)
		}
		
		# Should not overlap (all three axes must overlap)
		self.assertFalse(check_zone_overlap(zone1, zone2))
	
	def test_calculate_optimal_coverage_zones_no_overlap(self):
		"""Test zone calculation with no existing overlaps."""
		new_orientation: PoseMetricsDict = {
			'pitch': 10.0,
			'yaw': 20.0,
			'roll': 5.0
		}
		
		existing_zones = []
		new_quality = 0.8
		
		new_zone, updated_zones = calculate_optimal_coverage_zones(
			new_orientation,
			existing_zones,
			new_quality
		)
		
		# Should return new zone and empty existing zones
		self.assertIsNotNone(new_zone)
		self.assertEqual(len(updated_zones), 0)
		self.assertEqual(new_zone['pitch_range'], (-5.0, 25.0))
	
	def test_calculate_optimal_coverage_zones_with_overlap(self):
		"""Test zone calculation with existing overlaps."""
		new_orientation: PoseMetricsDict = {
			'pitch': 10.0,
			'yaw': 20.0,
			'roll': 5.0
		}
		
		existing_zone: CoverageZone = {
			'pitch_range': (0.0, 20.0),
			'yaw_range': (10.0, 30.0),
			'roll_range': (0.0, 15.0)
		}
		
		existing_zones = [existing_zone]
		new_quality = 0.8
		
		new_zone, updated_zones = calculate_optimal_coverage_zones(
			new_orientation,
			existing_zones,
			new_quality
		)
		
		# Should detect overlap and return zones
		self.assertIsNotNone(new_zone)
		self.assertEqual(len(updated_zones), 1)
	
	def test_get_zone_center(self):
		"""Test getting center of a zone."""
		zone: CoverageZone = {
			'pitch_range': (0.0, 20.0),
			'yaw_range': (10.0, 30.0),
			'roll_range': (-10.0, 10.0)
		}
		
		center = get_zone_center(zone)
		
		self.assertEqual(center['pitch'], 10.0)
		self.assertEqual(center['yaw'], 20.0)
		self.assertEqual(center['roll'], 0.0)
	
	def test_format_zone_description(self):
		"""Test zone description formatting."""
		zone: CoverageZone = {
			'pitch_range': (0.0, 20.0),
			'yaw_range': (10.0, 30.0),
			'roll_range': (-5.0, 5.0)
		}
		
		description = format_zone_description(zone)
		
		self.assertIn('Pitch', description)
		self.assertIn('Yaw', description)
		self.assertIn('Roll', description)
		self.assertIn('0.0', description)
		self.assertIn('20.0', description)


if __name__ == '__main__':
	unittest.main()
