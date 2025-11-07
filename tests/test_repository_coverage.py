"""Tests for repository coverage statistics."""

import tempfile

import pytest

from facefusion_repository.manager import RepositoryManager


@pytest.fixture
def temp_repo() -> str:
	"""Create temporary repository."""
	with tempfile.TemporaryDirectory() as tmpdir:
		yield tmpdir


def test_calculate_coverage_stats_empty_person(temp_repo: str) -> None:
	"""Test coverage stats for person with no faces."""
	manager = RepositoryManager(temp_repo)
	
	# Create person with no faces
	result = manager.create_person('Test Person', [])
	assert result['success']
	person_id = result['person_id']
	
	# Calculate coverage
	stats = manager.calculate_coverage_stats(person_id)
	
	assert stats['success']
	assert stats['total_faces'] == 0
	assert stats['unique_zones'] == 0
	assert stats['coverage_percentage'] == 0.0


def test_calculate_coverage_stats_nonexistent_person(temp_repo: str) -> None:
	"""Test coverage stats for nonexistent person."""
	manager = RepositoryManager(temp_repo)
	
	stats = manager.calculate_coverage_stats('fake-id-123')
	
	assert not stats['success']
	assert 'not found' in stats['message'].lower()


def test_calculate_coverage_stats_structure(temp_repo: str) -> None:
	"""Test coverage stats return structure."""
	manager = RepositoryManager(temp_repo)
	
	# Create person
	result = manager.create_person('Test Person', [])
	person_id = result['person_id']
	
	stats = manager.calculate_coverage_stats(person_id)
	
	# Verify structure
	assert 'success' in stats
	assert 'total_faces' in stats
	assert 'unique_zones' in stats
	assert 'coverage_percentage' in stats
	assert 'zone_distribution' in stats
	assert 'missing_zones' in stats
	
	# Verify types
	assert isinstance(stats['success'], bool)
	assert isinstance(stats['total_faces'], int)
	assert isinstance(stats['unique_zones'], int)
	assert isinstance(stats['coverage_percentage'], (int, float))
	assert isinstance(stats['zone_distribution'], dict)
	assert isinstance(stats['missing_zones'], list)


def test_calculate_coverage_percentage_bounds(temp_repo: str) -> None:
	"""Test coverage percentage is between 0 and 100."""
	manager = RepositoryManager(temp_repo)
	
	result = manager.create_person('Test Person', [])
	person_id = result['person_id']
	
	stats = manager.calculate_coverage_stats(person_id)
	
	assert 0.0 <= stats['coverage_percentage'] <= 100.0
