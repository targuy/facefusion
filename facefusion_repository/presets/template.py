"""
Preset template system for common configurations.
"""

from typing import Any, Dict, List, Optional

from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.manager import SettingsManager


class PresetTemplate:
    """Provides common preset templates and smart generation."""

    # Default settings templates
    DEFAULT_TEMPLATES = {
        'high_quality': {
            'processors': ['face_swapper'],
            'face_selector_mode': 'one',
            'face_selector_order': 'best-worst',
            'face_detector_model': 'yolo_face',
            'face_detector_size': '640x640',
            'face_detector_score': 0.5,
            'face_landmarker_model': '2dfan4',
            'face_landmarker_score': 0.5,
            'face_masker_types': ['box', 'region'],
            'face_mask_blur': 0.3,
            'face_mask_padding': [0, 0, 0, 0]
        },
        'fast_processing': {
            'processors': ['face_swapper'],
            'face_selector_mode': 'one',
            'face_selector_order': 'left-right',
            'face_detector_model': 'yunet',
            'face_detector_size': '320x320',
            'face_detector_score': 0.5,
            'face_landmarker_model': '2dfan4',
            'face_masker_types': ['box'],
            'face_mask_blur': 0.2
        },
        'enhanced_quality': {
            'processors': ['face_swapper', 'face_enhancer'],
            'face_selector_mode': 'one',
            'face_selector_order': 'best-worst',
            'face_detector_model': 'yolo_face',
            'face_detector_size': '960x960',
            'face_detector_score': 0.6,
            'face_landmarker_model': '2dfan4',
            'face_masker_types': ['occlusion', 'region'],
            'face_mask_blur': 0.4,
            'face_mask_padding': [5, 5, 5, 5]
        },
        'video_optimized': {
            'processors': ['face_swapper'],
            'face_selector_mode': 'many',
            'face_selector_order': 'left-right',
            'face_detector_model': 'yolo_face',
            'face_detector_size': '640x640',
            'face_detector_score': 0.5,
            'face_landmarker_model': '2dfan4',
            'face_masker_types': ['box', 'region'],
            'face_mask_blur': 0.3
        }
    }

    @classmethod
    def get_template(cls, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get settings template by name.

        Args:
            template_name: Template name

        Returns:
            Settings dictionary or None
        """
        return cls.DEFAULT_TEMPLATES.get(template_name)

    @classmethod
    def list_templates(cls) -> List[str]:
        """
        List available template names.

        Returns:
            List of template names
        """
        return list(cls.DEFAULT_TEMPLATES.keys())

    @classmethod
    def create_template_settings(
        cls,
        template_name: str,
        settings_manager: SettingsManager
    ) -> bool:
        """
        Create settings profile from template.

        Args:
            template_name: Template name
            settings_manager: Settings manager instance

        Returns:
            True if creation successful
        """
        template = cls.get_template(template_name)
        if template is None:
            print(f'Template not found: {template_name}')
            return False

        return settings_manager.create_profile(
            name=template_name,
            settings=template,
            description=f'Template: {template_name}',
            validate=True
        )

    @classmethod
    def generate_preset_from_template(
        cls,
        preset_name: str,
        face_id: str,
        template_name: str,
        repository_manager: RepositoryManager,
        settings_manager: SettingsManager
    ) -> bool:
        """
        Generate preset using a template.

        Args:
            preset_name: Preset name
            face_id: Face ID from repository
            template_name: Template name
            repository_manager: Repository manager
            settings_manager: Settings manager

        Returns:
            True if generation successful
        """
        # Create settings profile from template if it doesn't exist
        if settings_manager.get_profile(template_name) is None:
            if not cls.create_template_settings(template_name, settings_manager):
                return False

        # Create preset
        from facefusion_repository.presets.manager import PresetManager
        preset_manager = PresetManager(
            repository_manager=repository_manager,
            settings_manager=settings_manager
        )

        return preset_manager.create_preset(
            name=preset_name,
            face_id=face_id,
            settings_profile=template_name,
            description=f'Generated from {template_name} template',
            validate=True
        )

    @classmethod
    def generate_smart_presets(
        cls,
        repository_manager: RepositoryManager,
        settings_manager: SettingsManager,
        template_name: str = 'high_quality'
    ) -> int:
        """
        Auto-generate presets for all faces in repository using a template.

        Args:
            repository_manager: Repository manager
            settings_manager: Settings manager
            template_name: Template to use for all presets

        Returns:
            Number of presets created
        """
        # Get all faces
        faces = repository_manager.list_faces()
        if not faces:
            print('No faces found in repository')
            return 0

        # Create settings from template if needed
        if settings_manager.get_profile(template_name) is None:
            if not cls.create_template_settings(template_name, settings_manager):
                print(f'Failed to create template settings: {template_name}')
                return 0

        # Create preset for each face
        from facefusion_repository.presets.manager import PresetManager
        preset_manager = PresetManager(
            repository_manager=repository_manager,
            settings_manager=settings_manager
        )

        count = 0
        for face in faces:
            # Generate preset name
            face_name = face.metadata.name or f'Face {face.orientation_angle}°'
            preset_name = f'{face_name}_{template_name}'

            # Create preset
            if preset_manager.create_preset(
                name=preset_name,
                face_id=face.id,
                settings_profile=template_name,
                description=f'Auto-generated preset for {face_name}',
                validate=True
            ):
                count += 1

        print(f'Created {count} presets from {len(faces)} faces')
        return count

    @classmethod
    def generate_orientation_presets(
        cls,
        base_name: str,
        repository_manager: RepositoryManager,
        settings_manager: SettingsManager
    ) -> int:
        """
        Generate presets for different orientations of the same person.

        Args:
            base_name: Base name for preset series (e.g., "alice")
            repository_manager: Repository manager
            settings_manager: Settings manager

        Returns:
            Number of presets created
        """
        # Get all faces
        faces = repository_manager.list_faces()
        if not faces:
            print('No faces found in repository')
            return 0

        # Create high quality settings if needed
        template_name = 'high_quality'
        if settings_manager.get_profile(template_name) is None:
            if not cls.create_template_settings(template_name, settings_manager):
                return 0

        # Create presets for each orientation
        from facefusion_repository.presets.manager import PresetManager
        preset_manager = PresetManager(
            repository_manager=repository_manager,
            settings_manager=settings_manager
        )

        count = 0
        for face in faces:
            preset_name = f'{base_name}_{face.orientation_angle}deg'
            description = f'{base_name} at {face.orientation_angle}° orientation'

            if preset_manager.create_preset(
                name=preset_name,
                face_id=face.id,
                settings_profile=template_name,
                description=description,
                validate=True
            ):
                count += 1

        print(f'Created {count} orientation presets for {base_name}')
        return count
