"""
Tests for FaceFusion Repository System - Queue Processor.
"""

import pytest

from facefusion_repository.execution.queue_processor import QueueProcessor
from facefusion_repository.types import FrameFace
from facefusion.types import Face, BoundingBox, FaceLandmarkSet, FaceScoreSet
import numpy


def create_test_face() -> Face:
    """Create a test Face object."""
    return Face(
        bounding_box=numpy.array([100, 100, 300, 300]),
        score_set=FaceScoreSet(
            detector=0.9,
            landmarker=0.8
        ),
        landmark_set=FaceLandmarkSet(
            **{
                '5': numpy.zeros((5, 2)),
                '5/68': numpy.zeros((5, 2)),
                '68': numpy.zeros((68, 2)),
                '68/5': numpy.zeros((68, 2))
            }
        ),
        angle=0,
        embedding=numpy.zeros(512),
        embedding_norm=numpy.zeros(512),
        gender='female',
        age=range(25, 35),
        race='white'
    )


def create_test_frame_face(frame_number: int, video_path: str = 'test.mp4') -> FrameFace:
    """Create a test FrameFace object."""
    return FrameFace(
        face=create_test_face(),
        orientation=0,
        frame_number=frame_number,
        timestamp=frame_number / 30.0,
        video_path=video_path,
        matched_face_id='face_001'
    )


def test_queue_processor_initialization():
    """Test QueueProcessor initialization."""
    processor = QueueProcessor()

    assert processor.get_queue_count() == 0
    assert processor.get_total_items() == 0
    assert not processor.has_queues()


def test_queue_processor_add_to_queue():
    """Test adding items to queue."""
    processor = QueueProcessor()
    frame_face = create_test_frame_face(1)

    processor.add_to_queue('face_001', frame_face)

    assert processor.get_queue_count() == 1
    assert processor.get_total_items() == 1
    assert processor.has_queues()


def test_queue_processor_multiple_queues():
    """Test managing multiple queues."""
    processor = QueueProcessor()

    # Add items to different queues
    for face_id in ['face_001', 'face_002', 'face_003']:
        for i in range(5):
            frame_face = create_test_frame_face(i)
            processor.add_to_queue(face_id, frame_face)

    assert processor.get_queue_count() == 3
    assert processor.get_total_items() == 15


def test_queue_processor_get_queue():
    """Test retrieving specific queue."""
    processor = QueueProcessor()

    # Add items
    for i in range(10):
        frame_face = create_test_frame_face(i)
        processor.add_to_queue('face_001', frame_face)

    queue = processor.get_queue('face_001')

    assert len(queue) == 10


def test_queue_processor_get_nonexistent_queue():
    """Test retrieving non-existent queue."""
    processor = QueueProcessor()

    queue = processor.get_queue('nonexistent')

    assert queue == []


def test_queue_processor_clear_specific_queue():
    """Test clearing specific queue."""
    processor = QueueProcessor()

    # Add items to multiple queues
    processor.add_to_queue('face_001', create_test_frame_face(1))
    processor.add_to_queue('face_002', create_test_frame_face(2))

    processor.clear_queue('face_001')

    assert processor.get_queue_count() == 1
    assert len(processor.get_queue('face_001')) == 0
    assert len(processor.get_queue('face_002')) == 1


def test_queue_processor_clear_all_queues():
    """Test clearing all queues."""
    processor = QueueProcessor()

    # Add items
    processor.add_to_queue('face_001', create_test_frame_face(1))
    processor.add_to_queue('face_002', create_test_frame_face(2))

    processor.clear_queue()

    assert processor.get_queue_count() == 0
    assert processor.get_total_items() == 0


def test_queue_processor_statistics():
    """Test queue statistics."""
    processor = QueueProcessor()

    # Add different numbers of items to different queues
    for i in range(10):
        processor.add_to_queue('face_001', create_test_frame_face(i))
    for i in range(5):
        processor.add_to_queue('face_002', create_test_frame_face(i))

    stats = processor.get_queue_statistics()

    assert stats.total_queues == 2
    assert stats.total_faces == 15
    assert stats.faces_per_queue['face_001'] == 10
    assert stats.faces_per_queue['face_002'] == 5


def test_queue_processor_organize_by_video():
    """Test organizing queue by video."""
    processor = QueueProcessor()

    # Add frames from different videos
    for i in range(5):
        processor.add_to_queue('face_001', create_test_frame_face(i, 'video1.mp4'))
    for i in range(3):
        processor.add_to_queue('face_001', create_test_frame_face(i, 'video2.mp4'))

    organized = processor.organize_by_video('face_001')

    assert len(organized) == 2
    assert len(organized['video1.mp4']) == 5
    assert len(organized['video2.mp4']) == 3

    # Check that frames are sorted by frame number
    for i, frame_face in enumerate(organized['video1.mp4']):
        assert frame_face.frame_number == i


def test_queue_processor_priority_order():
    """Test getting queues in priority order."""
    processor = QueueProcessor()

    # Add different numbers of items (priority is by size, largest first)
    for i in range(10):
        processor.add_to_queue('face_001', create_test_frame_face(i))
    for i in range(5):
        processor.add_to_queue('face_002', create_test_frame_face(i))
    for i in range(15):
        processor.add_to_queue('face_003', create_test_frame_face(i))

    priority_order = processor.get_queue_priority_order()

    # Should be ordered by size: face_003 (15), face_001 (10), face_002 (5)
    assert priority_order[0] == 'face_003'
    assert priority_order[1] == 'face_001'
    assert priority_order[2] == 'face_002'


def test_queue_processor_get_all_queues():
    """Test getting all queues."""
    processor = QueueProcessor()

    # Add items
    processor.add_to_queue('face_001', create_test_frame_face(1))
    processor.add_to_queue('face_002', create_test_frame_face(2))

    all_queues = processor.get_all_queues()

    assert len(all_queues) == 2
    assert 'face_001' in all_queues
    assert 'face_002' in all_queues
