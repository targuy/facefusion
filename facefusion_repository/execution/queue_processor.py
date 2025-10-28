"""
Queue processor for organized batch execution.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.types import FaceEntry, FrameFace, QueueStats


class QueueProcessor:
    """
    Processes face swap queues organized by source face.

    This class manages processing queues where each queue contains
    destination faces matched to a specific source face.
    """

    def __init__(self, queue_path: Optional[str] = None) -> None:
        """
        Initialize queue processor.

        Args:
            queue_path: Path to queue storage directory. If None, uses default.
        """
        if queue_path is None:
            queue_path = os.path.expanduser('~/.facefusion_repository/queues')

        self.queue_path = Path(queue_path)
        self._queues: Dict[str, List[FrameFace]] = {}
        self._loaded = False

    def add_to_queue(self, face_id: str, frame_face: FrameFace) -> None:
        """
        Add a frame face to processing queue.

        Args:
            face_id: Source face ID for this queue
            frame_face: FrameFace to add to queue
        """
        if face_id not in self._queues:
            self._queues[face_id] = []

        self._queues[face_id].append(frame_face)

    def get_queue(self, face_id: str) -> List[FrameFace]:
        """
        Get processing queue for a specific face.

        Args:
            face_id: Source face ID

        Returns:
            List of FrameFace objects in the queue
        """
        return self._queues.get(face_id, [])

    def get_all_queues(self) -> Dict[str, List[FrameFace]]:
        """
        Get all processing queues.

        Returns:
            Dictionary mapping face IDs to their queues
        """
        return self._queues.copy()

    def get_queue_count(self) -> int:
        """
        Get number of queues.

        Returns:
            Number of queues
        """
        return len(self._queues)

    def get_total_items(self) -> int:
        """
        Get total number of items across all queues.

        Returns:
            Total number of FrameFace items
        """
        return sum(len(queue) for queue in self._queues.values())

    def get_queue_statistics(self) -> QueueStats:
        """
        Get statistics about current queues.

        Returns:
            QueueStats object with queue information
        """
        faces_per_queue = {
            face_id: len(queue)
            for face_id, queue in self._queues.items()
        }

        return QueueStats(
            total_queues=len(self._queues),
            total_faces=self.get_total_items(),
            faces_per_queue=faces_per_queue
        )

    def clear_queue(self, face_id: Optional[str] = None) -> None:
        """
        Clear specific queue or all queues.

        Args:
            face_id: Face ID of queue to clear. If None, clears all queues.
        """
        if face_id is None:
            self._queues.clear()
        elif face_id in self._queues:
            del self._queues[face_id]

    def save_queues(self, output_path: Optional[str] = None) -> bool:
        """
        Save queues to disk.

        Args:
            output_path: Path to save queues. If None, uses default location.

        Returns:
            True if save successful
        """
        if output_path is None:
            self.queue_path.mkdir(parents=True, exist_ok=True)
            output_path = str(self.queue_path / 'queues.json')

        try:
            # Convert queues to serializable format
            queues_data = {}
            for face_id, queue in self._queues.items():
                queues_data[face_id] = [
                    {
                        'orientation': ff.orientation,
                        'frame_number': ff.frame_number,
                        'timestamp': ff.timestamp,
                        'video_path': ff.video_path,
                        'matched_face_id': ff.matched_face_id
                        # Note: Cannot serialize the Face object directly
                    }
                    for ff in queue
                ]

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(queues_data, f, indent=2)

            return True

        except Exception as e:
            print(f'Error saving queues: {e}')
            return False

    def load_queues(self, input_path: Optional[str] = None) -> bool:
        """
        Load queues from disk.

        Args:
            input_path: Path to load queues from. If None, uses default location.

        Returns:
            True if load successful
        """
        if input_path is None:
            input_path = str(self.queue_path / 'queues.json')

        if not os.path.exists(input_path):
            print(f'Queue file not found: {input_path}')
            return False

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                queues_data = json.load(f)

            # Note: This only loads metadata, not the actual Face objects
            # Full queue reconstruction would require re-processing the videos
            self._queues.clear()
            for face_id, queue_items in queues_data.items():
                self._queues[face_id] = []
                # Queue items would need Face objects reconstructed
                # This is a simplified implementation

            self._loaded = True
            return True

        except Exception as e:
            print(f'Error loading queues: {e}')
            return False

    def organize_by_video(self, face_id: str) -> Dict[str, List[FrameFace]]:
        """
        Organize queue by video file.

        Args:
            face_id: Source face ID

        Returns:
            Dictionary mapping video paths to FrameFace lists
        """
        queue = self.get_queue(face_id)
        organized: Dict[str, List[FrameFace]] = {}

        for frame_face in queue:
            video_path = frame_face.video_path
            if video_path not in organized:
                organized[video_path] = []
            organized[video_path].append(frame_face)

        # Sort each video's frames by frame number
        for video_path in organized:
            organized[video_path].sort(key=lambda ff: ff.frame_number)

        return organized

    def get_queue_priority_order(self) -> List[str]:
        """
        Get face IDs in recommended processing order.

        Orders by queue size (largest first) for efficient processing.

        Returns:
            List of face IDs in priority order
        """
        return sorted(
            self._queues.keys(),
            key=lambda face_id: len(self._queues[face_id]),
            reverse=True
        )

    def has_queues(self) -> bool:
        """
        Check if any queues exist.

        Returns:
            True if queues exist
        """
        return len(self._queues) > 0
