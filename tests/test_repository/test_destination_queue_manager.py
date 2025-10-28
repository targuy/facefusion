"""
Tests for FaceFusion Repository System - Queue Manager.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

from facefusion_repository.destination.matcher import FaceMatch
from facefusion_repository.destination.queue_manager import ProcessingQueue, QueueManager
from facefusion_repository.types import FaceEntry, FaceMetadata, QualityMetrics


def create_test_face_entry(face_id: str, orientation: int, name: str = None) -> FaceEntry:
    """Create a test face entry."""
    return FaceEntry(
        id=face_id,
        file_path=f'/test/{face_id}.jpg',
        orientation_angle=orientation,
        quality_metrics=QualityMetrics(
            resolution=(512, 512),
            sharpness=0.7,
            detector_score=0.9,
            brightness=0.6,
            contrast=0.5,
            overall_quality=0.8
        ),
        face_embedding=np.zeros(512),
        face_landmarks={'5': [], '68': []},
        metadata=FaceMetadata(
            added_date='2025-10-28T00:00:00Z',
            name=name or f'Test Face {face_id}',
            tags=['test']
        )
    )


def create_mock_match(face_id: str, confidence: float = 0.8) -> FaceMatch:
    """Create a mock FaceMatch."""
    dest_face = Mock()
    dest_face.angle = 0.0
    
    repo_face = create_test_face_entry(face_id, 0)
    
    return FaceMatch(
        destination_face=dest_face,
        repository_face=repo_face,
        confidence=confidence,
        orientation_difference=5
    )


def test_processing_queue_creation():
    """Test ProcessingQueue creation."""
    queue = ProcessingQueue('face1', 'Test Person')
    
    assert queue.source_face_id == 'face1'
    assert queue.source_face_name == 'Test Person'
    assert queue.get_size() == 0
    assert queue.created_date is not None


def test_processing_queue_add_match():
    """Test adding matches to queue."""
    queue = ProcessingQueue('face1')
    match = create_mock_match('face1', confidence=0.85)
    
    queue.add_match(match, frame_number=10, timestamp=0.5, source_file='test.mp4')
    
    assert queue.get_size() == 1
    assert queue.matches[0]['confidence'] == 0.85
    assert queue.matches[0]['frame_number'] == 10
    assert queue.matches[0]['timestamp'] == 0.5
    assert queue.matches[0]['source_file'] == 'test.mp4'


def test_processing_queue_average_confidence():
    """Test average confidence calculation."""
    queue = ProcessingQueue('face1')
    
    # Empty queue
    assert queue.get_average_confidence() == 0.0
    
    # Add matches
    match1 = create_mock_match('face1', confidence=0.8)
    match2 = create_mock_match('face1', confidence=0.6)
    match3 = create_mock_match('face1', confidence=1.0)
    
    queue.add_match(match1)
    queue.add_match(match2)
    queue.add_match(match3)
    
    assert queue.get_average_confidence() == pytest.approx(0.8, 0.01)


def test_processing_queue_serialization():
    """Test queue serialization and deserialization."""
    queue = ProcessingQueue('face1', 'Test Person')
    match = create_mock_match('face1')
    queue.add_match(match, frame_number=5, timestamp=0.25)
    
    # Serialize
    queue_dict = queue.to_dict()
    
    assert queue_dict['source_face_id'] == 'face1'
    assert queue_dict['source_face_name'] == 'Test Person'
    assert queue_dict['match_count'] == 1
    assert len(queue_dict['matches']) == 1
    
    # Deserialize
    restored_queue = ProcessingQueue.from_dict(queue_dict)
    
    assert restored_queue.source_face_id == 'face1'
    assert restored_queue.source_face_name == 'Test Person'
    assert restored_queue.get_size() == 1


def test_queue_manager_initialization():
    """Test QueueManager initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = QueueManager(tmpdir)
        
        assert manager.repository_path == Path(tmpdir)
        assert manager.queues_dir == Path(tmpdir) / 'queues'
        assert manager.queues_dir.exists()


def test_queue_manager_create_queues():
    """Test creating queues from matches."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = QueueManager(tmpdir)
        
        matches = [
            create_mock_match('face1', 0.9),
            create_mock_match('face1', 0.8),
            create_mock_match('face2', 0.7)
        ]
        
        success = manager.create_queues_from_matches(
            matches,
            source_file='test.mp4',
            frame_numbers=[10, 20, 30],
            timestamps=[0.5, 1.0, 1.5]
        )
        
        assert success
        
        # Check queues were created
        queues = manager.list_queues()
        assert len(queues) == 2
        
        # Check face1 queue
        queue1 = manager.get_queue('face1')
        assert queue1 is not None
        assert queue1.get_size() == 2
        
        # Check face2 queue
        queue2 = manager.get_queue('face2')
        assert queue2 is not None
        assert queue2.get_size() == 1


def test_queue_manager_persistence():
    """Test queue persistence to disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create queues
        manager1 = QueueManager(tmpdir)
        matches = [create_mock_match('face1', 0.9)]
        manager1.create_queues_from_matches(matches, 'test.mp4')
        
        # Load queues in new instance
        manager2 = QueueManager(tmpdir)
        queues = manager2.list_queues()
        
        assert len(queues) == 1
        assert queues[0].source_face_id == 'face1'
        assert queues[0].get_size() == 1


def test_queue_manager_clear_queue():
    """Test clearing a specific queue."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = QueueManager(tmpdir)
        
        matches = [
            create_mock_match('face1'),
            create_mock_match('face2')
        ]
        manager.create_queues_from_matches(matches, 'test.mp4')
        
        # Clear face1 queue
        success = manager.clear_queue('face1')
        assert success
        
        queues = manager.list_queues()
        assert len(queues) == 1
        assert queues[0].source_face_id == 'face2'


def test_queue_manager_clear_all_queues():
    """Test clearing all queues."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = QueueManager(tmpdir)
        
        matches = [
            create_mock_match('face1'),
            create_mock_match('face2')
        ]
        manager.create_queues_from_matches(matches, 'test.mp4')
        
        # Clear all queues
        success = manager.clear_all_queues()
        assert success
        
        queues = manager.list_queues()
        assert len(queues) == 0


def test_queue_manager_get_statistics():
    """Test queue statistics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = QueueManager(tmpdir)
        
        matches = [
            create_mock_match('face1'),
            create_mock_match('face1'),
            create_mock_match('face2')
        ]
        manager.create_queues_from_matches(matches, 'test.mp4')
        
        stats = manager.get_statistics()
        
        assert stats.total_queues == 2
        assert stats.total_faces == 3
        assert stats.faces_per_queue['face1'] == 2
        assert stats.faces_per_queue['face2'] == 1


def test_queue_manager_export_queue():
    """Test exporting a queue to JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = QueueManager(tmpdir)
        
        matches = [create_mock_match('face1')]
        manager.create_queues_from_matches(matches, 'test.mp4')
        
        export_path = os.path.join(tmpdir, 'exported_queue.json')
        success = manager.export_queue('face1', export_path)
        
        assert success
        assert os.path.exists(export_path)
        
        # Verify exported data
        with open(export_path, 'r') as f:
            data = json.load(f)
        
        assert data['source_face_id'] == 'face1'
        assert data['match_count'] == 1


def test_queue_manager_export_nonexistent_queue():
    """Test exporting a queue that doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = QueueManager(tmpdir)
        
        export_path = os.path.join(tmpdir, 'exported_queue.json')
        success = manager.export_queue('nonexistent', export_path)
        
        assert not success
        assert not os.path.exists(export_path)
