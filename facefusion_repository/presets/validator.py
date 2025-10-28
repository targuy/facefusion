"""
Preset validator for face-settings compatibility.
"""

from typing import List, Optional

from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.manager import SettingsManager
from facefusion_repository.types import ValidationResult


class PresetValidator:
    """Validates preset face and settings references."""

    def __init__(
        self,
        repository_manager: RepositoryManager,
        settings_manager: SettingsManager
    ) -> None:
        """
        Initialize validator.

        Args:
            repository_manager: Repository manager instance
            settings_manager: Settings manager instance
        """
        self.repository_manager = repository_manager
        self.settings_manager = settings_manager

    def validate_preset(
        self,
        face_id: str,
        settings_profile: str
    ) -> ValidationResult:
        """
        Validate complete preset configuration.

        Args:
            face_id: Face ID to validate
            settings_profile: Settings profile name to validate

        Returns:
            ValidationResult with validation status
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Validate face reference
        face_result = self.validate_face_reference(face_id)
        errors.extend(face_result.errors)
        warnings.extend(face_result.warnings)

        # Validate settings reference
        settings_result = self.validate_settings_reference(settings_profile)
        errors.extend(settings_result.errors)
        warnings.extend(settings_result.warnings)

        # Validate compatibility
        if not errors:
            compat_result = self.validate_compatibility(face_id, settings_profile)
            errors.extend(compat_result.errors)
            warnings.extend(compat_result.warnings)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def validate_face_reference(self, face_id: str) -> ValidationResult:
        """
        Validate face reference exists in repository.

        Args:
            face_id: Face ID to validate

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Check if face exists
        face_entry = self.repository_manager.get_face(face_id)
        if face_entry is None:
            errors.append(f'Face not found in repository: {face_id}')
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Check face quality
        if face_entry.quality_metrics.overall_quality < 0.5:
            warnings.append(
                f'Face quality is below recommended level: '
                f'{face_entry.quality_metrics.overall_quality:.2f} < 0.50'
            )

        # Check if face file still exists
        import os
        if not os.path.exists(face_entry.file_path):
            errors.append(f'Face file not found: {face_entry.file_path}')

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def validate_settings_reference(self, settings_profile: str) -> ValidationResult:
        """
        Validate settings reference exists.

        Args:
            settings_profile: Settings profile name to validate

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Check if settings profile exists
        profile = self.settings_manager.get_profile(settings_profile)
        if profile is None:
            errors.append(f'Settings profile not found: {settings_profile}')
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Validate settings content
        from facefusion_repository.settings.validator import SettingsValidator
        settings = profile.get('settings', {})
        settings_result = SettingsValidator.validate_settings(settings)

        errors.extend(settings_result.errors)
        warnings.extend(settings_result.warnings)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def validate_compatibility(
        self,
        face_id: str,
        settings_profile: str
    ) -> ValidationResult:
        """
        Validate face-settings compatibility.

        Args:
            face_id: Face ID
            settings_profile: Settings profile name

        Returns:
            ValidationResult
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Get face and settings
        face_entry = self.repository_manager.get_face(face_id)
        profile = self.settings_manager.get_profile(settings_profile)

        if face_entry is None or profile is None:
            errors.append('Cannot validate compatibility: missing face or settings')
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        settings = profile.get('settings', {})

        # Check resolution compatibility
        min_resolution = settings.get('output_image_resolution')
        if min_resolution:
            face_res = face_entry.quality_metrics.resolution
            if face_res[0] < 512 or face_res[1] < 512:
                warnings.append(
                    f'Face resolution {face_res} may be low for high-quality output'
                )

        # Check processor compatibility
        processors = settings.get('processors', [])
        if 'face_swapper' not in processors:
            warnings.append('Settings do not include face_swapper processor')

        # Check if face quality meets settings requirements
        detector_score_threshold = settings.get('face_detector_score', 0.5)
        if face_entry.quality_metrics.detector_score < detector_score_threshold:
            warnings.append(
                f'Face detector score {face_entry.quality_metrics.detector_score:.2f} '
                f'is below settings threshold {detector_score_threshold}'
            )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def validate_orientation_coverage(
        self,
        presets: List[str]
    ) -> ValidationResult:
        """
        Validate orientation coverage for a list of presets.

        Args:
            presets: List of preset names

        Returns:
            ValidationResult with coverage information
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Standard orientations
        standard_orientations = [0, 45, 90, 135, 180, 225, 270, 315]
        covered_orientations = set()

        # Check each preset
        from facefusion_repository.presets.manager import PresetManager
        preset_manager = PresetManager(
            repository_manager=self.repository_manager,
            settings_manager=self.settings_manager
        )

        for preset_name in presets:
            preset = preset_manager.get_preset(preset_name)
            if preset is None:
                errors.append(f'Preset not found: {preset_name}')
                continue

            face_entry = self.repository_manager.get_face(preset.face_id)
            if face_entry:
                covered_orientations.add(face_entry.orientation_angle)

        # Check coverage
        missing_orientations = set(standard_orientations) - covered_orientations
        if missing_orientations:
            warnings.append(
                f'Missing orientation coverage: {sorted(missing_orientations)}'
            )

        coverage_pct = len(covered_orientations) / len(standard_orientations) * 100
        if coverage_pct < 50:
            warnings.append(f'Low orientation coverage: {coverage_pct:.1f}%')

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
