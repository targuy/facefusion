"""Settings profile management for repository system."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SettingsManager:
	"""Manage settings profiles for FaceFusion repository operations."""

	def __init__(self, repository_path: str = None):
		"""
		Initialize settings manager.
		
		Args:
			repository_path: Path to repository root (default: .face_repository)
		"""
		if repository_path is None:
			repository_path = '.face_repository'
		self.repository_path = Path(repository_path)
		self.settings_dir = self.repository_path / 'settings'
		self.settings_dir.mkdir(parents=True, exist_ok=True)
		self.settings_file = self.settings_dir / 'profiles.json'
		
		# Initialize with built-in templates if file doesn't exist
		if not self.settings_file.exists():
			self._initialize_builtin_templates()

	def _initialize_builtin_templates(self) -> None:
		"""Initialize built-in settings templates."""
		builtin_templates = {
			'high_quality': {
				'description': 'High quality processing with best results',
				'settings': {
					'face_detector_model': 'retinaface',
					'face_detector_score': 0.6,
					'face_recognizer_model': 'arcface_blendswap',
					'reference_face_distance': 0.5,
					'face_mask_types': ['box', 'region', 'occlusion'],
					'quality_threshold': 0.8,
					'orientation_tolerance': 15.0,
					'face_selector_mode': 'best-quality'
				}
			},
			'fast_processing': {
				'description': 'Fast processing with good quality balance',
				'settings': {
					'face_detector_model': 'yolo_face',
					'face_detector_score': 0.5,
					'face_recognizer_model': 'arcface_inswapper',
					'reference_face_distance': 0.6,
					'face_mask_types': ['box'],
					'quality_threshold': 0.6,
					'orientation_tolerance': 20.0,
					'face_selector_mode': 'first'
				}
			},
			'gpu_optimized': {
				'description': 'Optimized for GPU processing',
				'settings': {
					'face_detector_model': 'retinaface',
					'face_detector_score': 0.5,
					'face_recognizer_model': 'arcface_inswapper',
					'reference_face_distance': 0.55,
					'face_mask_types': ['box', 'region'],
					'quality_threshold': 0.7,
					'orientation_tolerance': 18.0,
					'face_selector_mode': 'all',
					'execution_providers': ['cuda']
				}
			}
		}
		
		self._save_profiles(builtin_templates)

	def _load_profiles(self) -> Dict[str, Dict[str, Any]]:
		"""Load all settings profiles from storage."""
		if not self.settings_file.exists():
			return {}
		
		try:
			with open(self.settings_file, 'r') as f:
				return json.load(f)
		except (json.JSONDecodeError, IOError):
			return {}

	def _save_profiles(self, profiles: Dict[str, Dict[str, Any]]) -> None:
		"""Save all settings profiles to storage."""
		with open(self.settings_file, 'w') as f:
			json.dump(profiles, f, indent=2)

	def create_profile(
		self,
		name: str,
		settings: Dict[str, Any],
		description: str = ''
	) -> bool:
		"""
		Create a new settings profile.
		
		Args:
			name: Profile name
			settings: Dictionary of settings to save
			description: Optional description of the profile
		
		Returns:
			True if successful, False if profile already exists
		"""
		profiles = self._load_profiles()
		
		if name in profiles:
			return False
		
		profiles[name] = {
			'description': description,
			'settings': settings
		}
		
		self._save_profiles(profiles)
		return True

	def update_profile(
		self,
		name: str,
		settings: Dict[str, Any],
		description: Optional[str] = None
	) -> bool:
		"""
		Update an existing settings profile.
		
		Args:
			name: Profile name
			settings: Dictionary of settings to update
			description: Optional new description
		
		Returns:
			True if successful, False if profile doesn't exist
		"""
		profiles = self._load_profiles()
		
		if name not in profiles:
			return False
		
		profiles[name]['settings'] = settings
		if description is not None:
			profiles[name]['description'] = description
		
		self._save_profiles(profiles)
		return True

	def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
		"""
		Get a settings profile by name.
		
		Args:
			name: Profile name
		
		Returns:
			Profile data or None if not found
		"""
		profiles = self._load_profiles()
		return profiles.get(name)

	def list_profiles(self) -> List[str]:
		"""
		List all available profile names.
		
		Returns:
			List of profile names
		"""
		profiles = self._load_profiles()
		return list(profiles.keys())

	def delete_profile(self, name: str) -> bool:
		"""
		Delete a settings profile.
		
		Args:
			name: Profile name
		
		Returns:
			True if successful, False if profile doesn't exist
		"""
		profiles = self._load_profiles()
		
		if name not in profiles:
			return False
		
		del profiles[name]
		self._save_profiles(profiles)
		return True

	def get_builtin_templates(self) -> List[str]:
		"""
		Get list of built-in template names.
		
		Returns:
			List of built-in template names
		"""
		return ['high_quality', 'fast_processing', 'gpu_optimized']

	def apply_profile(self, name: str) -> Optional[Dict[str, Any]]:
		"""
		Get settings from a profile for application.
		
		Args:
			name: Profile name
		
		Returns:
			Settings dictionary or None if profile not found
		"""
		profile = self.get_profile(name)
		if profile:
			return profile['settings']
		return None

	def export_profile(self, name: str, output_path: str) -> bool:
		"""
		Export a profile to a JSON file.
		
		Args:
			name: Profile name
			output_path: Path to output JSON file
		
		Returns:
			True if successful, False otherwise
		"""
		profile = self.get_profile(name)
		if not profile:
			return False
		
		try:
			with open(output_path, 'w') as f:
				json.dump(profile, f, indent=2)
			return True
		except IOError:
			return False

	def import_profile(self, name: str, input_path: str) -> bool:
		"""
		Import a profile from a JSON file.
		
		Args:
			name: Profile name to create
			input_path: Path to input JSON file
		
		Returns:
			True if successful, False otherwise
		"""
		try:
			with open(input_path, 'r') as f:
				profile_data = json.load(f)
			
			settings = profile_data.get('settings', {})
			description = profile_data.get('description', '')
			
			return self.create_profile(name, settings, description)
		except (json.JSONDecodeError, IOError, KeyError):
			return False
