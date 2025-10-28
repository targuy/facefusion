"""File management utilities for repository"""

import os
import shutil
from typing import Optional


class FileManager:
	"""Manages file operations for repository"""
	
	def __init__(self, repository_path : str = '.facefusion_repository'):
		self.repository_path = repository_path
		self.faces_dir = os.path.join(repository_path, 'faces')
	
	def copy_face_image(self, source_path : str, person_id : str, face_id : str) -> Optional[str]:
		"""Copy face image to repository"""
		try:
			person_dir = os.path.join(self.faces_dir, person_id)
			os.makedirs(person_dir, exist_ok=True)
			
			ext = os.path.splitext(source_path)[1]
			dest_filename = f"{face_id}{ext}"
			dest_path = os.path.join(person_dir, dest_filename)
			
			shutil.copy2(source_path, dest_path)
			return dest_path
		except Exception:
			return None
	
	def get_face_path(self, person_id : str, face_id : str, ext : str = '.jpg') -> str:
		"""Get path for face image"""
		return os.path.join(self.faces_dir, person_id, f"{face_id}{ext}")
	
	def face_exists(self, person_id : str, face_id : str) -> bool:
		"""Check if face file exists"""
		face_dir = os.path.join(self.faces_dir, person_id)
		if not os.path.exists(face_dir):
			return False
		
		for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
			if os.path.exists(os.path.join(face_dir, f"{face_id}{ext}")):
				return True
		return False
	
	def remove_person_files(self, person_id : str) -> bool:
		"""Remove all files for a person"""
		try:
			person_dir = os.path.join(self.faces_dir, person_id)
			if os.path.exists(person_dir):
				shutil.rmtree(person_dir)
			return True
		except Exception:
			return False
