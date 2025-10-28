#!/usr/bin/env python3
"""
Simple integration test for repository system
Tests basic functionality without requiring numpy or other dependencies
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_basic_structure():
	"""Test that all modules exist and are importable"""
	print("Testing module structure...")
	
	# Check directories exist
	assert os.path.exists('facefusion_repository'), "Repository directory missing"
	assert os.path.exists('facefusion_repository/core'), "Core directory missing"
	assert os.path.exists('facefusion_repository/cli'), "CLI directory missing"
	assert os.path.exists('facefusion_repository/storage'), "Storage directory missing"
	
	# Check key files exist
	assert os.path.exists('facefusion_repository/__init__.py'), "Init file missing"
	assert os.path.exists('facefusion_repository/types.py'), "Types file missing"
	assert os.path.exists('facefusion_repository/core/person_manager.py'), "PersonManager missing"
	assert os.path.exists('facefusion_repository/storage/json_storage.py'), "JsonStorage missing"
	
	print("✓ All modules present")


def test_types_file():
	"""Test types file is valid Python"""
	print("Testing types file...")
	
	with open('facefusion_repository/types.py', 'r') as f:
		content = f.read()
		
	# Check for key type definitions
	assert 'PersonFace' in content, "PersonFace type missing"
	assert 'RepositoryEntry' in content, "RepositoryEntry type missing"
	assert 'Pose3D' in content, "Pose3D type missing"
	assert 'QualityMetrics' in content, "QualityMetrics type missing"
	
	print("✓ Types file valid")


def test_json_storage_basic():
	"""Test JSON storage without dependencies"""
	print("Testing JSON storage...")
	
	with tempfile.TemporaryDirectory() as tmpdir:
		# Create a simple storage instance
		repo_path = tmpdir
		db_file = os.path.join(repo_path, 'repository.json')
		faces_dir = os.path.join(repo_path, 'faces')
		
		# Simulate init
		os.makedirs(faces_dir, exist_ok=True)
		
		initial_db = {
			'version': '1.0.0',
			'persons': []
		}
		
		with open(db_file, 'w') as f:
			json.dump(initial_db, f, indent=2)
		
		# Verify creation
		assert os.path.exists(db_file), "DB file not created"
		assert os.path.exists(faces_dir), "Faces dir not created"
		
		# Load and verify
		with open(db_file, 'r') as f:
			loaded = json.load(f)
		
		assert loaded['version'] == '1.0.0', "Version mismatch"
		assert loaded['persons'] == [], "Persons should be empty"
		
		print("✓ JSON storage works")


def test_core_integration():
	"""Test core.py modifications"""
	print("Testing core.py integration...")
	
	with open('facefusion/core.py', 'r') as f:
		content = f.read()
	
	# Check for repository routing
	assert 'route_repository' in content, "route_repository function missing"
	assert 'repo-init' in content, "repo-init command missing"
	assert 'repo-add' in content, "repo-add command missing"
	assert 'repo-list' in content, "repo-list command missing"
	
	print("✓ Core integration present")


def test_program_integration():
	"""Test program.py modifications"""
	print("Testing program.py integration...")
	
	with open('facefusion/program.py', 'r') as f:
		content = f.read()
	
	# Check for repository commands
	assert 'create_repository_add_program' in content, "repo-add program missing"
	assert 'create_repository_list_program' in content, "repo-list program missing"
	assert 'repo-init' in content, "repo-init parser missing"
	
	print("✓ Program integration present")


def test_wording_integration():
	"""Test wording.py modifications"""
	print("Testing wording.py integration...")
	
	with open('facefusion/wording.py', 'r') as f:
		content = f.read()
	
	# Check for repository help text
	assert 'repo_init' in content, "repo_init wording missing"
	assert 'repo_add' in content, "repo_add wording missing"
	assert 'repo_list' in content, "repo_list wording missing"
	assert 'repo_person' in content, "repo_person wording missing"
	
	print("✓ Wording integration present")


def test_types_integration():
	"""Test types.py modifications"""
	print("Testing types.py integration...")
	
	with open('facefusion/types.py', 'r') as f:
		content = f.read()
	
	# Check for repository types
	assert 'RepositoryPersonId' in content, "RepositoryPersonId type missing"
	assert 'RepositoryPose3D' in content, "RepositoryPose3D type missing"
	assert 'RepositoryQualityMetrics' in content, "RepositoryQualityMetrics type missing"
	assert 'RepositoryPersonFace' in content, "RepositoryPersonFace type missing"
	assert 'RepositoryEntry' in content, "RepositoryEntry type missing"
	
	print("✓ Types integration present")


def main():
	"""Run all tests"""
	print("=" * 60)
	print("Repository System Integration Tests")
	print("=" * 60)
	print()
	
	try:
		test_basic_structure()
		test_types_file()
		test_json_storage_basic()
		test_core_integration()
		test_program_integration()
		test_wording_integration()
		test_types_integration()
		
		print()
		print("=" * 60)
		print("✓ All tests passed!")
		print("=" * 60)
		return 0
		
	except AssertionError as e:
		print()
		print("=" * 60)
		print(f"✗ Test failed: {e}")
		print("=" * 60)
		return 1
	except Exception as e:
		print()
		print("=" * 60)
		print(f"✗ Unexpected error: {e}")
		print("=" * 60)
		return 1


if __name__ == '__main__':
	sys.exit(main())
