"""
Profile comparator for analyzing settings differences.
"""

from typing import Any, Dict, List, Tuple

from facefusion_repository.types import ProfileComparison, SettingsProfile


class ProfileComparator:
    """Compare settings profiles and highlight differences."""

    @staticmethod
    def compare_profiles(
        profile1: SettingsProfile,
        profile2: SettingsProfile
    ) -> ProfileComparison:
        """
        Compare two settings profiles.

        Args:
            profile1: First profile
            profile2: Second profile

        Returns:
            ProfileComparison with detailed differences
        """
        settings1 = profile1.settings
        settings2 = profile2.settings

        # Find keys in each profile
        keys1 = set(settings1.keys())
        keys2 = set(settings2.keys())

        # Common keys
        common_keys = keys1 & keys2

        # Keys only in one profile
        only_in_profile1 = {k: settings1[k] for k in keys1 - keys2}
        only_in_profile2 = {k: settings2[k] for k in keys2 - keys1}

        # Compare common settings
        common_settings: Dict[str, Any] = {}
        different_settings: Dict[str, Tuple[Any, Any]] = {}

        for key in common_keys:
            value1 = settings1[key]
            value2 = settings2[key]

            if value1 == value2:
                common_settings[key] = value1
            else:
                different_settings[key] = (value1, value2)

        identical = (
            len(different_settings) == 0 and
            len(only_in_profile1) == 0 and
            len(only_in_profile2) == 0
        )

        return ProfileComparison(
            profile1_name=profile1.name,
            profile2_name=profile2.name,
            identical=identical,
            common_settings=common_settings,
            different_settings=different_settings,
            only_in_profile1=only_in_profile1,
            only_in_profile2=only_in_profile2
        )

    @staticmethod
    def format_comparison(comparison: ProfileComparison) -> str:
        """
        Format comparison result as readable text.

        Args:
            comparison: ProfileComparison object

        Returns:
            Formatted comparison string
        """
        lines: List[str] = []

        lines.append('=' * 70)
        lines.append(f'Profile Comparison: "{comparison.profile1_name}" vs "{comparison.profile2_name}"')
        lines.append('=' * 70)
        lines.append('')

        if comparison.identical:
            lines.append('✓ Profiles are identical')
            return '\n'.join(lines)

        # Show different settings
        if comparison.different_settings:
            lines.append('Different Settings:')
            lines.append('-' * 70)
            for key, (value1, value2) in sorted(comparison.different_settings.items()):
                lines.append(f'  {key}:')
                lines.append(f'    {comparison.profile1_name}: {value1}')
                lines.append(f'    {comparison.profile2_name}: {value2}')
            lines.append('')

        # Show settings only in profile 1
        if comparison.only_in_profile1:
            lines.append(f'Only in "{comparison.profile1_name}":')
            lines.append('-' * 70)
            for key, value in sorted(comparison.only_in_profile1.items()):
                lines.append(f'  {key}: {value}')
            lines.append('')

        # Show settings only in profile 2
        if comparison.only_in_profile2:
            lines.append(f'Only in "{comparison.profile2_name}":')
            lines.append('-' * 70)
            for key, value in sorted(comparison.only_in_profile2.items()):
                lines.append(f'  {key}: {value}')
            lines.append('')

        # Show common settings summary
        if comparison.common_settings:
            lines.append(f'Common Settings: {len(comparison.common_settings)} identical')
            lines.append('')

        return '\n'.join(lines)

    @staticmethod
    def get_differences_summary(comparison: ProfileComparison) -> Dict[str, int]:
        """
        Get summary statistics of differences.

        Args:
            comparison: ProfileComparison object

        Returns:
            Dictionary with difference counts
        """
        return {
            'total_settings': (
                len(comparison.common_settings) +
                len(comparison.different_settings) +
                len(comparison.only_in_profile1) +
                len(comparison.only_in_profile2)
            ),
            'common_identical': len(comparison.common_settings),
            'different_values': len(comparison.different_settings),
            'only_in_profile1': len(comparison.only_in_profile1),
            'only_in_profile2': len(comparison.only_in_profile2)
        }

    @staticmethod
    def highlight_critical_differences(
        comparison: ProfileComparison
    ) -> List[str]:
        """
        Identify critical differences that significantly affect behavior.

        Args:
            comparison: ProfileComparison object

        Returns:
            List of critical differences
        """
        critical_settings = {
            'processors',
            'face_detector_model',
            'face_detector_score',
            'face_selector_mode',
            'execution_providers',
            'output_video_encoder'
        }

        critical_diffs: List[str] = []

        for key, (value1, value2) in comparison.different_settings.items():
            if key in critical_settings:
                critical_diffs.append(
                    f'{key}: {value1} -> {value2}'
                )

        for key in comparison.only_in_profile1:
            if key in critical_settings:
                critical_diffs.append(
                    f'{key}: present in {comparison.profile1_name}, missing in {comparison.profile2_name}'
                )

        for key in comparison.only_in_profile2:
            if key in critical_settings:
                critical_diffs.append(
                    f'{key}: missing in {comparison.profile1_name}, present in {comparison.profile2_name}'
                )

        return critical_diffs
