"""
Progress tracking for batch processing operations.

Provides real-time progress monitoring, ETA calculation, and status reporting
for batch face swap operations.
"""

import time
from typing import Optional


class ProgressTracker:
    """Tracks progress of batch processing operations."""

    def __init__(self, total_items: int):
        """
        Initialize progress tracker.

        Args:
            total_items: Total number of items to process
        """
        self.total_items = total_items
        self.completed_items = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time

    def update(self, increment: int = 1) -> None:
        """
        Update progress counter.

        Args:
            increment: Number of items completed since last update
        """
        self.completed_items += increment
        self.last_update_time = time.time()

    def get_progress_percentage(self) -> float:
        """
        Get current progress as percentage.

        Returns:
            Progress percentage (0.0-100.0)
        """
        if self.total_items == 0:
            return 100.0
        return (self.completed_items / self.total_items) * 100.0

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since start.

        Returns:
            Elapsed time in seconds
        """
        return time.time() - self.start_time

    def get_eta(self) -> Optional[float]:
        """
        Estimate time remaining.

        Returns:
            Estimated time remaining in seconds, or None if cannot estimate
        """
        if self.completed_items == 0:
            return None

        elapsed = self.get_elapsed_time()
        rate = self.completed_items / elapsed
        remaining = self.total_items - self.completed_items

        if rate > 0:
            return remaining / rate
        return None

    def get_items_per_second(self) -> float:
        """
        Get processing rate.

        Returns:
            Items processed per second
        """
        elapsed = self.get_elapsed_time()
        if elapsed > 0:
            return self.completed_items / elapsed
        return 0.0

    def get_progress_string(self) -> str:
        """
        Get formatted progress string.

        Returns:
            Human-readable progress string
        """
        percentage = self.get_progress_percentage()
        elapsed = self.get_elapsed_time()
        eta = self.get_eta()

        progress_str = f"{self.completed_items}/{self.total_items} ({percentage:.1f}%)"
        progress_str += f" - Elapsed: {self._format_time(elapsed)}"

        if eta is not None:
            progress_str += f" - ETA: {self._format_time(eta)}"

        return progress_str

    def _format_time(self, seconds: float) -> str:
        """
        Format time duration.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def is_complete(self) -> bool:
        """
        Check if processing is complete.

        Returns:
            True if all items processed
        """
        return self.completed_items >= self.total_items

    def reset(self) -> None:
        """Reset progress tracker."""
        self.completed_items = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
