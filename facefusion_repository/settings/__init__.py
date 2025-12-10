"""
Settings management module for FaceFusion Repository System.

Manages settings profiles for face swapping operations.
"""

from .manager import SettingsManager
from .types import SettingsProfile, FaceSwapperSettings

__all__ = [
    'SettingsManager',
    'SettingsProfile',
    'FaceSwapperSettings'
]
