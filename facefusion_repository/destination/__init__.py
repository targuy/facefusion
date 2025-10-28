"""
Destination face processing module for FaceFusion Repository System.

This module handles analysis of destination media (images/videos), extracts faces,
matches them with repository faces, and creates processing queues.
"""

from facefusion_repository.destination.analyzer import DestinationAnalyzer
from facefusion_repository.destination.extractor import FaceExtractor
from facefusion_repository.destination.matcher import RepositoryMatcher
from facefusion_repository.destination.queue_manager import QueueManager

__all__ = [
    'DestinationAnalyzer',
    'FaceExtractor',
    'RepositoryMatcher',
    'QueueManager'
]
