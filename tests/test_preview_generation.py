"""Unit tests for preview generation functionality."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from facefusion_repository.preview import (
	PreviewGenerator,
	PreviewResult,
	ComparisonResult,
	generate_import_preview
)


class TestPreviewGeneration(unittest.TestCase):
	"""Test preview generation functions."""
	
	def setUp(self):
		"""Set up test fixtures."""
		self.temp_dir = tempfile.mkdtemp()
		
		# Create dummy face files
		self.source_face = os.path.join(self.temp_dir, 'source.jpg')
		self.test_face = os.path.join(self.temp_dir, 'test.jpg')
		
		Path(self.source_face).touch()
		Path(self.test_face).touch()
	
	def tearDown(self):
		"""Clean up test fixtures."""
		import shutil
		if os.path.exists(self.temp_dir):
			shutil.rmtree(self.temp_dir)
	
	def test_preview_result_initialization(self):
		"""Test PreviewResult initialization."""
		result = PreviewResult(
			'/path/to/preview.jpg',
			True,
			'Success',
			0.85,
			'/path/to/test.jpg'
		)
		
		self.assertEqual(result.preview_path, '/path/to/preview.jpg')
		self.assertTrue(result.success)
		self.assertEqual(result.message, 'Success')
		self.assertEqual(result.quality_score, 0.85)
		self.assertEqual(result.test_face_path, '/path/to/test.jpg')
	
	def test_preview_result_to_dict(self):
		"""Test PreviewResult to_dict conversion."""
		result = PreviewResult(
			'/path/to/preview.jpg',
			True,
			'Success',
			0.85,
			'/path/to/test.jpg'
		)
		
		result_dict = result.to_dict()
		
		self.assertIsInstance(result_dict, dict)
		self.assertEqual(result_dict['preview_path'], '/path/to/preview.jpg')
		self.assertEqual(result_dict['success'], True)
		self.assertEqual(result_dict['quality_score'], 0.85)
	
	def test_comparison_result_initialization(self):
		"""Test ComparisonResult initialization."""
		existing = PreviewResult('/existing.jpg', True, 'OK', 0.7, '/test.jpg')
		new = PreviewResult('/new.jpg', True, 'OK', 0.9, '/test.jpg')
		
		comparison = ComparisonResult('/test.jpg', existing, new)
		
		self.assertEqual(comparison.test_face_path, '/test.jpg')
		self.assertEqual(comparison.existing_preview, existing)
		self.assertEqual(comparison.new_preview, new)
		self.assertEqual(comparison.winner, 'new')  # new has higher quality
	
	def test_comparison_result_winner_existing(self):
		"""Test ComparisonResult when existing wins."""
		existing = PreviewResult('/existing.jpg', True, 'OK', 0.9, '/test.jpg')
		new = PreviewResult('/new.jpg', True, 'OK', 0.7, '/test.jpg')
		
		comparison = ComparisonResult('/test.jpg', existing, new)
		
		self.assertEqual(comparison.winner, 'existing')
	
	def test_preview_generator_initialization(self):
		"""Test PreviewGenerator initialization."""
		generator = PreviewGenerator()
		self.assertIsNotNone(generator)
	
	def test_generate_face_swap_preview_missing_source(self):
		"""Test preview generation with missing source face."""
		generator = PreviewGenerator()
		
		result = generator.generate_face_swap_preview(
			['/nonexistent/source.jpg'],
			self.test_face
		)
		
		self.assertFalse(result.success)
		self.assertIn('not found', result.message.lower())
	
	def test_generate_face_swap_preview_missing_target(self):
		"""Test preview generation with missing target."""
		generator = PreviewGenerator()
		
		result = generator.generate_face_swap_preview(
			[self.source_face],
			'/nonexistent/target.jpg'
		)
		
		self.assertFalse(result.success)
		self.assertIn('not found', result.message.lower())
	
	def test_generate_face_swap_preview_no_sources(self):
		"""Test preview generation with no source faces."""
		generator = PreviewGenerator()
		
		result = generator.generate_face_swap_preview(
			[],
			self.test_face
		)
		
		self.assertFalse(result.success)
		self.assertIn('no source', result.message.lower())
	
	def test_generate_face_swap_preview_valid_inputs(self):
		"""Test preview generation with valid inputs."""
		generator = PreviewGenerator()
		
		result = generator.generate_face_swap_preview(
			[self.source_face],
			self.test_face
		)
		
		# Should succeed with placeholder implementation or fail gracefully with imports
		# In test environment, FaceFusion modules may not be available
		if result.success:
			self.assertIsNotNone(result.preview_path)
		else:
			# If failed, it should be due to import issues
			self.assertIn('import', result.message.lower())
	
	def test_generate_import_preview(self):
		"""Test import preview generation."""
		test_faces = [self.test_face]
		
		results = generate_import_preview(
			self.source_face,
			test_faces
		)
		
		self.assertIsInstance(results, dict)
		self.assertIn(self.test_face, results)
		self.assertIsInstance(results[self.test_face], PreviewResult)
	
	def test_generate_import_preview_missing_test_face(self):
		"""Test import preview with missing test face."""
		test_faces = ['/nonexistent/test.jpg']
		
		results = generate_import_preview(
			self.source_face,
			test_faces
		)
		
		self.assertIsInstance(results, dict)
		self.assertIn('/nonexistent/test.jpg', results)
		self.assertFalse(results['/nonexistent/test.jpg'].success)
	
	def test_generate_import_preview_multiple_test_faces(self):
		"""Test import preview with multiple test faces."""
		# Create additional test faces
		test_face2 = os.path.join(self.temp_dir, 'test2.jpg')
		Path(test_face2).touch()
		
		test_faces = [self.test_face, test_face2]
		
		results = generate_import_preview(
			self.source_face,
			test_faces
		)
		
		self.assertEqual(len(results), 2)
		self.assertIn(self.test_face, results)
		self.assertIn(test_face2, results)


if __name__ == '__main__':
	unittest.main()
