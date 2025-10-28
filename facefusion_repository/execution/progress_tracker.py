"""
Progress tracking for batch execution.
"""

import time
from typing import Optional


class ProgressTracker:
    """Tracks batch processing progress and estimates completion time."""

    def __init__(self, total_items: int) -> None:
        """
        Initialize progress tracker.

        Args:
            total_items: Total number of items to process
        """
        self.total_items = total_items
        self.completed_items = 0
        self.failed_items = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self._paused = False
        self._pause_time: Optional[float] = None
        self._total_pause_duration = 0.0

    def update(self, completed: int, failed: int = 0) -> None:
        """
        Update progress.

        Args:
            completed: Number of newly completed items
            failed: Number of newly failed items
        """
        if self._paused:
            return

        self.completed_items += completed
        self.failed_items += failed
        self.last_update_time = time.time()

    def pause(self) -> None:
        """Pause the progress tracker."""
        if not self._paused:
            self._paused = True
            self._pause_time = time.time()

    def resume(self) -> None:
        """Resume the progress tracker."""
        if self._paused and self._pause_time:
            self._total_pause_duration += time.time() - self._pause_time
            self._paused = False
            self._pause_time = None

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time in seconds, excluding pause time.

        Returns:
            Elapsed time in seconds
        """
        current_time = time.time()
        elapsed = current_time - self.start_time - self._total_pause_duration

        if self._paused and self._pause_time:
            elapsed -= (current_time - self._pause_time)

        return max(0.0, elapsed)

    def get_eta(self) -> Optional[float]:
        """
        Estimate time remaining in seconds.

        Returns:
            Estimated seconds remaining, or None if cannot estimate
        """
        if self.completed_items == 0:
            return None

        elapsed = self.get_elapsed_time()
        if elapsed <= 0:
            return None

        items_per_second = self.completed_items / elapsed
        remaining_items = self.total_items - (self.completed_items + self.failed_items)

        if items_per_second <= 0:
            return None

        return remaining_items / items_per_second

    def get_progress_percentage(self) -> float:
        """
        Get progress as percentage.

        Returns:
            Progress percentage (0.0 to 100.0)
        """
        if self.total_items == 0:
            return 100.0

        processed = self.completed_items + self.failed_items
        return min(100.0, (processed / self.total_items) * 100.0)

    def get_success_rate(self) -> float:
        """
        Get success rate as percentage.

        Returns:
            Success rate percentage (0.0 to 100.0)
        """
        processed = self.completed_items + self.failed_items
        if processed == 0:
            return 0.0

        return (self.completed_items / processed) * 100.0

    def get_progress_string(self) -> str:
        """
        Get formatted progress string.

        Returns:
            Human-readable progress string
        """
        processed = self.completed_items + self.failed_items
        percentage = self.get_progress_percentage()
        elapsed = self.get_elapsed_time()

        progress_str = f'{processed}/{self.total_items} ({percentage:.1f}%) - '
        progress_str += f'Success: {self.completed_items}, Failed: {self.failed_items}'

        # Add time information
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            progress_str += f' - Elapsed: {hours}h {minutes}m {seconds}s'
        elif minutes > 0:
            progress_str += f' - Elapsed: {minutes}m {seconds}s'
        else:
            progress_str += f' - Elapsed: {seconds}s'

        # Add ETA if available
        eta = self.get_eta()
        if eta is not None:
            eta_hours, eta_remainder = divmod(int(eta), 3600)
            eta_minutes, eta_seconds = divmod(eta_remainder, 60)

            if eta_hours > 0:
                progress_str += f' - ETA: {eta_hours}h {eta_minutes}m {eta_seconds}s'
            elif eta_minutes > 0:
                progress_str += f' - ETA: {eta_minutes}m {eta_seconds}s'
            else:
                progress_str += f' - ETA: {eta_seconds}s'

        if self._paused:
            progress_str += ' [PAUSED]'

        return progress_str

    def is_complete(self) -> bool:
        """
        Check if processing is complete.

        Returns:
            True if all items processed
        """
        return (self.completed_items + self.failed_items) >= self.total_items

    def is_paused(self) -> bool:
        """
        Check if tracker is paused.

        Returns:
            True if paused
        """
        return self._paused

    def get_statistics(self) -> dict:
        """
        Get detailed statistics.

        Returns:
            Dictionary with processing statistics
        """
        elapsed = self.get_elapsed_time()
        processed = self.completed_items + self.failed_items

        items_per_second = self.completed_items / elapsed if elapsed > 0 else 0.0

        return {
            'total_items': self.total_items,
            'completed_items': self.completed_items,
            'failed_items': self.failed_items,
            'processed_items': processed,
            'remaining_items': self.total_items - processed,
            'progress_percentage': self.get_progress_percentage(),
            'success_rate': self.get_success_rate(),
            'elapsed_time': elapsed,
            'eta': self.get_eta(),
            'items_per_second': items_per_second,
            'is_paused': self._paused,
            'is_complete': self.is_complete()
        }
