"""
Tests for FaceFusion Repository System - Progress Tracker.
"""

import time

import pytest

from facefusion_repository.execution.progress_tracker import ProgressTracker


def test_progress_tracker_initialization():
    """Test ProgressTracker initialization."""
    tracker = ProgressTracker(100)

    assert tracker.total_items == 100
    assert tracker.completed_items == 0
    assert tracker.failed_items == 0
    assert not tracker.is_complete()
    assert not tracker.is_paused()


def test_progress_tracker_update():
    """Test updating progress."""
    tracker = ProgressTracker(100)

    tracker.update(10, 2)

    assert tracker.completed_items == 10
    assert tracker.failed_items == 2
    assert tracker.get_progress_percentage() == 12.0
    assert not tracker.is_complete()


def test_progress_tracker_completion():
    """Test progress completion."""
    tracker = ProgressTracker(10)

    tracker.update(8, 2)

    assert tracker.is_complete()
    assert tracker.get_progress_percentage() == 100.0


def test_progress_tracker_success_rate():
    """Test success rate calculation."""
    tracker = ProgressTracker(100)

    tracker.update(80, 20)

    assert tracker.get_success_rate() == 80.0


def test_progress_tracker_pause_resume():
    """Test pause and resume functionality."""
    tracker = ProgressTracker(100)

    assert not tracker.is_paused()

    tracker.pause()
    assert tracker.is_paused()

    # Updates should be ignored while paused
    tracker.update(10, 0)
    assert tracker.completed_items == 0

    tracker.resume()
    assert not tracker.is_paused()

    # Updates should work after resume
    tracker.update(10, 0)
    assert tracker.completed_items == 10


def test_progress_tracker_elapsed_time():
    """Test elapsed time calculation."""
    tracker = ProgressTracker(10)

    time.sleep(0.1)

    elapsed = tracker.get_elapsed_time()
    assert elapsed >= 0.1
    assert elapsed < 0.2  # Allow some margin


def test_progress_tracker_eta():
    """Test ETA calculation."""
    tracker = ProgressTracker(100)

    # No items completed yet, ETA should be None
    assert tracker.get_eta() is None

    # Complete some items
    tracker.update(25, 0)

    # Wait a bit so elapsed time is measurable
    time.sleep(0.1)

    eta = tracker.get_eta()
    # ETA should be available and positive
    assert eta is not None
    assert eta > 0


def test_progress_tracker_progress_string():
    """Test progress string formatting."""
    tracker = ProgressTracker(100)

    tracker.update(50, 10)

    progress_str = tracker.get_progress_string()

    assert '60/100' in progress_str
    assert '60.0%' in progress_str
    assert 'Success: 50' in progress_str
    assert 'Failed: 10' in progress_str


def test_progress_tracker_statistics():
    """Test statistics dictionary."""
    tracker = ProgressTracker(100)

    tracker.update(60, 15)

    stats = tracker.get_statistics()

    assert stats['total_items'] == 100
    assert stats['completed_items'] == 60
    assert stats['failed_items'] == 15
    assert stats['processed_items'] == 75
    assert stats['remaining_items'] == 25
    assert stats['progress_percentage'] == 75.0
    assert stats['success_rate'] == 80.0
    assert not stats['is_paused']
    assert not stats['is_complete']


def test_progress_tracker_zero_items():
    """Test tracker with zero items."""
    tracker = ProgressTracker(0)

    assert tracker.get_progress_percentage() == 100.0
    assert tracker.is_complete()


def test_progress_tracker_pause_time_exclusion():
    """Test that pause time is excluded from elapsed time."""
    tracker = ProgressTracker(10)

    time.sleep(0.1)
    tracker.pause()
    time.sleep(0.2)
    tracker.resume()

    elapsed = tracker.get_elapsed_time()

    # Elapsed should be around 0.1s, not 0.3s
    assert elapsed < 0.15
