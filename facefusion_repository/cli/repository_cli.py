"""CLI commands for FaceFusion Repository"""

import hashlib
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List

from facefusion_repository.core.face_analyzer import FaceAnalyzer
from facefusion_repository.core.person_manager import PersonManager
from facefusion_repository.core.quality_assessor import QualityAssessor
from facefusion_repository.storage.file_manager import FileManager
from facefusion_repository.types import PersonFace


class RepositoryCLI:
	"""Command-line interface for repository operations"""
	
	def __init__(self, repository_path : str = '.facefusion_repository'):
		self.repository_path = repository_path
		self.person_manager = PersonManager(repository_path)
		self.quality_assessor = QualityAssessor()
		self.face_analyzer = FaceAnalyzer()
		self.file_manager = FileManager(repository_path)
	
	def init_repository(self) -> Dict[str, Any]:
		"""Initialize repository"""
		result = self.person_manager.init_repository()
		return result
	
	def add_face(self, source_path : str, person_name : str, preview : bool = False) -> Dict[str, Any]:
		"""Add a face to repository"""
		# Check if repository exists
		if not self.person_manager.repository_exists():
			return\
			{
				'success': False,
				'message': 'Repository not initialized. Run repo-init first.',
				'data': None
			}
		
		# Check if file exists
		if not os.path.exists(source_path):
			return\
			{
				'success': False,
				'message': f'Source file not found: {source_path}',
				'data': None
			}
		
		# Get or create person
		person_id = self._get_or_create_person(person_name)
		if not person_id:
			return\
			{
				'success': False,
				'message': f'Failed to get or create person: {person_name}',
				'data': None
			}
		
		# This would integrate with FaceFusion's face detection in actual implementation
		# For now, we create a placeholder
		face_id = self._generate_face_id()
		
		# Copy face image to repository
		face_path = self.file_manager.copy_face_image(source_path, person_id, face_id)
		if not face_path:
			return\
			{
				'success': False,
				'message': 'Failed to copy face image to repository',
				'data': None
			}
		
		# Create face data with placeholder values
		# In real implementation, this would use FaceFusion's face detection
		face_data : PersonFace =\
		{
			'face_id': face_id,
			'person_id': person_id,
			'image_path': source_path,
			'face_path': face_path,
			'pose_3d':\
			{
				'yaw': 0.0,
				'pitch': 0.0,
				'roll': 0.0,
				'confidence': 0.8
			},
			'quality':\
			{
				'sharpness': 0.8,
				'brightness': 0.7,
				'overall_quality': 0.75,
				'has_occlusion': False
			},
			'embedding': [],  # type: ignore[typeddict-item]
			'added_date': datetime.now().isoformat(),
			'tags': []
		}
		
		# Add face to person
		result = self.person_manager.add_face_to_person(person_id, face_data)
		
		if result['success'] and preview:
			result['message'] += f'\nFace quality: {face_data["quality"]["overall_quality"]:.2f}'
		
		return result
	
	def list_persons(self) -> Dict[str, Any]:
		"""List all persons in repository"""
		if not self.person_manager.repository_exists():
			return\
			{
				'success': False,
				'message': 'Repository not initialized',
				'data': None
			}
		
		persons = self.person_manager.list_persons()
		
		return\
		{
			'success': True,
			'message': f'Found {len(persons)} person(s)',
			'data': {'persons': persons}
		}
	
	def list_faces(self, person_name : str) -> Dict[str, Any]:
		"""List faces for a person"""
		if not self.person_manager.repository_exists():
			return\
			{
				'success': False,
				'message': 'Repository not initialized',
				'data': None
			}
		
		# Find person by name
		persons = self.person_manager.list_persons()
		person = None
		for p in persons:
			if p['person_name'].lower() == person_name.lower():
				person = p
				break
		
		if not person:
			return\
			{
				'success': False,
				'message': f'Person "{person_name}" not found',
				'data': None
			}
		
		faces = self.person_manager.get_faces_for_person(person['person_id'])
		
		return\
		{
			'success': True,
			'message': f'Found {len(faces)} face(s) for {person_name}',
			'data': {'person': person, 'faces': faces}
		}
	
	def _get_or_create_person(self, person_name : str) -> str:
		"""Get existing person ID or create new person"""
		persons = self.person_manager.list_persons()
		
		# Check if person exists
		for person in persons:
			if person['person_name'].lower() == person_name.lower():
				return person['person_id']
		
		# Create new person
		result = self.person_manager.add_person(person_name)
		if result['success'] and result['data']:
			return result['data']['person_id']
		return ''
	
	def _generate_face_id(self) -> str:
		"""Generate unique face ID"""
		return f"face_{uuid.uuid4().hex[:12]}"
