"""Unit tests for test faces management."""

import os
import tempfile
import unittest
from pathlib import Path

from facefusion_repository.test_faces import (
	get_test_faces_directory,
	get_test_faces,
	create_test_faces_directory,
	add_test_face,
	list_test_faces_info
)


class TestTestFacesManagement(unittest.TestCase):
	"""Test test faces management functions."""
	
	def setUp(self):
		"""Set up test fixtures."""
		self.temp_dir = tempfile.mkdtemp()
		self.test_faces_dir = os.path.join(self.temp_dir, 'test_faces')
	
	def tearDown(self):
		"""Clean up test fixtures."""
		import shutil
		if os.path.exists(self.temp_dir):
			shutil.rmtree(self.temp_dir)
	
	def test_get_test_faces_directory_custom(self):
		"""Test getting custom test faces directory."""
		test_dir = get_test_faces_directory(self.test_faces_dir)
		
		self.assertEqual(str(test_dir), self.test_faces_dir)
	
	def test_get_test_faces_directory_default(self):
		"""Test getting default test faces directory."""
		test_dir = get_test_faces_directory()
		
		self.assertIsNotNone(test_dir)
		self.assertIsInstance(test_dir, Path)
	
	def test_create_test_faces_directory(self):
		"""Test creating test faces directory."""
		test_dir = create_test_faces_directory(self.test_faces_dir)
		
		self.assertTrue(test_dir.exists())
		self.assertTrue(test_dir.is_dir())
		
		# Check that README was created
		readme_path = test_dir / 'README.md'
		self.assertTrue(readme_path.exists())
	
	def test_get_test_faces_empty_directory(self):
		"""Test getting test faces from empty directory."""
		create_test_faces_directory(self.test_faces_dir)
		
		test_faces = get_test_faces(self.test_faces_dir)
		
		# Should return empty list (only README exists, not an image)
		self.assertEqual(len(test_faces), 0)
	
	def test_get_test_faces_nonexistent_directory(self):
		"""Test getting test faces from nonexistent directory."""
		test_faces = get_test_faces('/nonexistent/dir')
		
		self.assertEqual(len(test_faces), 0)
	
	def test_get_test_faces_with_images(self):
		"""Test getting test faces with actual images."""
		create_test_faces_directory(self.test_faces_dir)
		
		# Create dummy image files
		test_dir = Path(self.test_faces_dir)
		(test_dir / 'face1.jpg').touch()
		(test_dir / 'face2.png').touch()
		(test_dir / 'face3.jpeg').touch()
		
		test_faces = get_test_faces(self.test_faces_dir)
		
		self.assertEqual(len(test_faces), 3)
		self.assertTrue(any('face1.jpg' in f for f in test_faces))
		self.assertTrue(any('face2.png' in f for f in test_faces))
	
	def test_get_test_faces_max_count(self):
		"""Test getting test faces with max count limit."""
		create_test_faces_directory(self.test_faces_dir)
		
		# Create more files than max_count
		test_dir = Path(self.test_faces_dir)
		for i in range(10):
			(test_dir / f'face{i}.jpg').touch()
		
		test_faces = get_test_faces(self.test_faces_dir, max_count=3)
		
		self.assertEqual(len(test_faces), 3)
	
	def test_get_test_faces_filters_non_images(self):
		"""Test that non-image files are filtered out."""
		create_test_faces_directory(self.test_faces_dir)
		
		test_dir = Path(self.test_faces_dir)
		(test_dir / 'face1.jpg').touch()
		(test_dir / 'document.txt').touch()
		(test_dir / 'data.json').touch()
		
		test_faces = get_test_faces(self.test_faces_dir)
		
		# Only image file should be included
		self.assertEqual(len(test_faces), 1)
		self.assertTrue(test_faces[0].endswith('.jpg'))
	
	def test_add_test_face(self):
		"""Test adding a test face."""
		create_test_faces_directory(self.test_faces_dir)
		
		# Create a source face
		source_face = os.path.join(self.temp_dir, 'source.jpg')
		Path(source_face).touch()
		
		success = add_test_face(source_face, self.test_faces_dir)
		
		self.assertTrue(success)
		
		# Verify file was copied
		test_faces = get_test_faces(self.test_faces_dir)
		self.assertEqual(len(test_faces), 1)
		self.assertTrue(test_faces[0].endswith('source.jpg'))
	
	def test_add_test_face_nonexistent_source(self):
		"""Test adding nonexistent test face."""
		create_test_faces_directory(self.test_faces_dir)
		
		success = add_test_face('/nonexistent/face.jpg', self.test_faces_dir)
		
		self.assertFalse(success)
	
	def test_add_test_face_creates_directory(self):
		"""Test that add_test_face creates directory if needed."""
		# Create source face but not test faces directory
		source_face = os.path.join(self.temp_dir, 'source.jpg')
		Path(source_face).touch()
		
		success = add_test_face(source_face, self.test_faces_dir)
		
		self.assertTrue(success)
		self.assertTrue(Path(self.test_faces_dir).exists())
	
	def test_list_test_faces_info(self):
		"""Test listing test faces with info."""
		create_test_faces_directory(self.test_faces_dir)
		
		# Create test face
		test_dir = Path(self.test_faces_dir)
		test_face = test_dir / 'face1.jpg'
		test_face.write_text('dummy content')
		
		info_list = list_test_faces_info(self.test_faces_dir)
		
		self.assertEqual(len(info_list), 1)
		self.assertIn('path', info_list[0])
		self.assertIn('name', info_list[0])
		self.assertIn('size', info_list[0])
		self.assertEqual(info_list[0]['name'], 'face1.jpg')
		self.assertGreater(info_list[0]['size'], 0)
	
	def test_list_test_faces_info_empty(self):
		"""Test listing test faces info from empty directory."""
		create_test_faces_directory(self.test_faces_dir)
		
		info_list = list_test_faces_info(self.test_faces_dir)
		
		self.assertEqual(len(info_list), 0)


if __name__ == '__main__':
	unittest.main()
